"""Relatórios GA4 de leitura. runReport usa POST por exigência da API Google."""
import argparse
from datetime import date
import json
import os
import re
import sys
import urllib.error
import urllib.request
from .client import NoRedirect


class GA4Error(RuntimeError):
    pass


def report_body(start, end, offset=0):
    try:
        if date.fromisoformat(start) > date.fromisoformat(end):
            raise ValueError
    except (ValueError, TypeError):
        raise GA4Error('Use datas ISO válidas e início anterior ao fim.') from None
    return {
        'dateRanges': [{'startDate': start, 'endDate': end}],
        'dimensions': [{'name': n} for n in (
            'sessionCampaignName', 'sessionSourceMedium', 'landingPagePlusQueryString')],
        'metrics': [{'name': n} for n in (
            'sessions', 'engagedSessions', 'engagementRate', 'keyEvents', 'totalRevenue')],
        'limit': '10000', 'offset': str(offset),
        'orderBys': [{'dimension': {'dimensionName': n}} for n in (
            'sessionCampaignName', 'sessionSourceMedium', 'landingPagePlusQueryString')],
    }


class GA4Client:
    def __init__(self, token=None, opener=None):
        self._token = token or os.environ.get('GA4_ACCESS_TOKEN')
        if not self._token:
            raise GA4Error('Configure GA4_ACCESS_TOKEN nos segredos do ambiente.')
        self._opener = opener or urllib.request.build_opener(NoRedirect())

    def report(self, property_id, start, end):
        if not re.fullmatch(r'[0-9]+', property_id):
            raise GA4Error('A propriedade deve ser um ID numérico, não G-….')
        body = report_body(start, end)
        url = f'https://analyticsdata.googleapis.com/v1beta/properties/{property_id}:runReport'
        rows = []
        while True:
            request = urllib.request.Request(url, method='POST',
                data=json.dumps(body).encode(), headers={
                    'Authorization': 'Bearer ' + self._token,
                    'Content-Type': 'application/json'})
            try:
                with self._opener.open(request, timeout=45) as response:
                    result = json.load(response)
            except urllib.error.HTTPError as exc:
                raise GA4Error(f'GA4 HTTP {exc.code}; verifique acesso, token e API habilitada.') from None
            except (OSError, ValueError):
                raise GA4Error('Falha de rede ou JSON inválido do GA4.') from None
            page = result.get('rows', [])
            rows.extend(page)
            if len(rows) >= result.get('rowCount', 0):
                break
            if not page:
                raise GA4Error('Paginação GA4 incompleta.')
            body['offset'] = str(len(rows))
        return {'property': property_id, 'start': start, 'end': end,
                'dimensionHeaders': result.get('dimensionHeaders', []),
                'metricHeaders': result.get('metricHeaders', []),
                'metadata': result.get('metadata', {}), 'rows': rows,
                'rowCount': len(rows)}


def main():
    parser = argparse.ArgumentParser(description='Relatório GA4 somente leitura (POST runReport).')
    parser.add_argument('--property', required=True)
    parser.add_argument('--start', required=True)
    parser.add_argument('--end', required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(GA4Client().report(args.property, args.start, args.end),
                         ensure_ascii=False, indent=2))
    except GA4Error as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
