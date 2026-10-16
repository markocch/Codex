import argparse
import json
import sys
from .client import MetaClient, MetaError


def main():
    parser = argparse.ArgumentParser(description='Relatório Meta Ads, somente GET.')
    parser.add_argument('--account', default='act_184261823230641')
    parser.add_argument('--period', default='last_30d',
                        choices=['last_30d', 'last_7d', 'today', 'yesterday', 'maximum'])
    args = parser.parse_args()
    try:
        report = MetaClient().report(args.account, args.period)
    except MetaError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
