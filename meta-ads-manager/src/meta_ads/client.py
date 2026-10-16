import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request


class MetaError(RuntimeError):
    pass


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class MetaClient:
    def __init__(self, token=None, opener=None):
        self._token = token or os.environ.get('META_ACCESS_TOKEN')
        if not self._token:
            raise MetaError('META_ACCESS_TOKEN não configurado.')
        self._opener = opener or urllib.request.build_opener(NoRedirect())

    def get(self, path, **params):
        if not re.fullmatch(r'[a-zA-Z0-9_/]+', path):
            raise MetaError('Caminho inválido.')
        url = 'https://graph.facebook.com/v26.0/' + path
        url += '?' + urllib.parse.urlencode(params)
        request = urllib.request.Request(url, method='GET', headers={
            'Authorization': 'Bearer ' + self._token,
        })
        try:
            with self._opener.open(request, timeout=45) as response:
                return json.load(response)
        except urllib.error.HTTPError as exc:
            # Nunca imprimir corpo, URL ou cabeçalhos potencialmente sensíveis.
            try:
                error = json.load(exc).get('error', {})
            except (ValueError, TypeError):
                error = {}
            code = error.get('code')
            code = code if isinstance(code, int) else 'desconhecido'
            raise MetaError(f'Meta HTTP {exc.code}; código {code}.') from None
        except (OSError, ValueError):
            raise MetaError('Falha de rede ou resposta JSON inválida.') from None

    def pages(self, path, **params):
        seen = set()
        while True:
            result = self.get(path, **params)
            yield from result.get('data', [])
            paging = result.get('paging', {})
            cursor = paging.get('cursors', {}).get('after')
            if not paging.get('next'):
                return
            # Não seguir paging.next: pode conter token ou outro domínio.
            if not cursor or cursor in seen:
                raise MetaError('Paginação inválida ou repetida.')
            seen.add(cursor)
            params['after'] = cursor

    def report(self, account='act_184261823230641', period='last_30d'):
        if not re.fullmatch(r'act_[0-9]+', account):
            raise MetaError('Conta inválida.')
        if period not in ('last_30d', 'last_7d', 'yesterday', 'today', 'maximum'):
            raise MetaError('Período inválido.')
        info = self.get(account, fields='id,name,currency,timezone_name,account_status')
        campaigns = list(self.pages(account + '/campaigns',
            fields='id,name,status,effective_status,objective,daily_budget,lifetime_budget', limit=100))
        insights = list(self.pages(account + '/insights', level='campaign', date_preset=period,
            fields='campaign_id,campaign_name,date_start,date_stop,spend,impressions,reach,clicks,inline_link_clicks,ctr,cpc,cpm,actions,cost_per_action_type', limit=100))
        metrics = {item['campaign_id']: item for item in insights}
        return {'account': info, 'period': period,
                'campaigns': [dict(c, insights=metrics.pop(c['id'], None)) for c in campaigns],
                'insights_without_campaign': list(metrics.values())}
