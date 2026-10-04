```python
def process_bounties(data):
    items = data.split('#### ')
    result = []
    for item in items:
        if item.strip() == '':
            continue
        parts = item.split(' - ')
        if len(parts) < 3:
            continue
        id_part = parts[0].strip()
        title = parts[1].strip('[]').strip()
        repo = parts[2].strip()
        comments = parts[3].strip().split(' - ')[0].strip().split('Comments: ')[1].strip()
        last_updated = parts[3].strip().split(' - ')[1].strip().split('Last Updated: ')[1].strip()
        result.append({
            'id': id_part,
            'title': title,
            'repository': repo,
            'comments': comments,
            'last_updated': last_updated
        })
    return result

# Example usage:
# data = """### Active Bounty Scan Results

# **Scan Time:** 2026-10-04 19:11 UTC

# 1. [🎯 Bounty Alert: 10 New Opportunityies found](https://github.com/freedom-winds/BountyScout/issues/1194)
# - **Repository:** [freedom-winds/BountyScout](https://github.com/freedom-winds/BountyScout)
# - **Comments:** 0
# - **Last Updated:** 2026-10-04T19:10:54Z

# 2. [Sync VAD overwrites distinct WAL audio when speech starts at the same timestamp](https://github.com/BasedHardware/omi/issues/20686)
# - **Repository:** [BasedHardware/omi](https://github.com/BasedHardware/omi)
# - **Comments:** 0
# - **Last Updated:** 2026-10-04T19:10:52Z

# 3. [Make trader and convoy robbery a moderately profitable mid-game route](https://github.com/btseytlin/road-machiners/issues/157)
# - **Repository:** [btseytlin/road-machiners](https://github.com/btseytlin/road-machiners)
# - **Comments:** 7
# - **Last Updated:** 2026-10-04T19:10:17Z

# 4. [Inability to complete bounty](https://github.com/Alliance-codeBase/PostMeta/issues/250)
# - **Repository:** [Alliance-codeBase/PostMeta](https://github.com/Alliance-codeBase/PostMeta)
# - **Comments:** 0
# - **Last Updated:** 2026-10-04T19:05:46Z

# 5. [[Bounty 100 USDT] Refactor Signature Verifier & Add Replay Attack Invariant Tests](https://github.com/muhammalif/evm-signature-verifier/issues/1)
# - **Repository:** [muhammalif/evm-signature-verifier](https://github.com/muhammalif/evm-signature-verifier)
# - **Comments:** 2
# - **Last Updated:** 2026-10-04T18:54:41Z

# 6. [Railway 赏金：有 9 条值得抢](https://github.com/HCTDIP/corps-jobs/issues/45)
# - **Repository:** [HCTDIP/corps-jobs](https://github.com/HCTDIP/corps-jobs)
# - **Comments:** 0
# - **Last Updated:** 2026-10-04T18:48:17Z

# 7. [I cannot find anywhere on the actual Tormentor that it gives gold bounty](https://github.com/ValveSoftware/Dota2-Gameplay/issues/35531)
# - **Repository:** [ValveSoftware/Dota2-Gameplay](https://github.com/ValveSoftware/Dota2-Gameplay)
# - **Comments:** 3
# - **Last Updated:** 2026-10-04T18:44:16Z

# 8. [Mult"""
# processed_data = process_bounties(data)
# print(processed_data)
```