import sys
sys.path.insert(0, 'backend')
import github_service, requests, json

query = """
query ($login: String!) {
  user(login: $login) {
    contributionsCollection {
      totalCommitContributions
      totalPullRequestContributions
      totalIssueContributions
      totalRepositoryContributions
      totalPullRequestReviewContributions
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            date
            contributionCount
            weekday
            color
          }
        }
      }
    }
  }
}
"""

resp = requests.post(
    github_service.GRAPHQL_ENDPOINT,
    json={"query": query, "variables": {"login": "kriss2012"}},
    headers=github_service._get_headers()
)
res = resp.json()
col = res.get("data", {}).get("user", {}).get("contributionsCollection", {})
cal = col.get("contributionCalendar", {})
print("Rolling Total Contributions:", cal.get("totalContributions"))
weeks = cal.get("weeks", [])
print("Rolling Weeks count:", len(weeks))
if weeks:
    print("Week 0 first day:", weeks[0]["contributionDays"][0])
    print("Week -1 last day:", weeks[-1]["contributionDays"][-1])
    active_in_weeks = sum(1 for w in weeks for d in w["contributionDays"] if d["contributionCount"] > 0)
    print("Active days in last year:", active_in_weeks)
