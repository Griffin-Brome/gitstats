import pandas as pd


class StatsCalculator:

    def __init__(self, statsCollector):
        self.statsCollecter = statsCollector

    def get_start(self):
        return self.statsCollecter.get_start()

    def get_end(self):
        return self.statsCollecter.get_end()

    def getPRsByAssignee(self):
        return self.statsCollecter.getPRs().groupby(['assignee']).agg({
            'id': 'count'
        }).reset_index().rename(columns={
            'id': 'assigned'
        }).sort_values(by="assigned", ascending=False)

    def getCommentsByUser(self):
        comments = self.statsCollecter.getComments().groupby(['user']).agg({
            'id': 'count'
        }).reset_index().rename(columns={
            'id': 'comments'
        }).sort_values(by="comments", ascending=False)

        for user in self.getUsers():
            if len(comments[comments["user"] == user]) == 0:
                comments = comments.append({
                    "user": user,
                    "comments": 0
                },
                                           ignore_index=True)

        return comments

    def getCommitsByUser(self):
        commits = self.statsCollecter.getCommits().groupby(['user']).agg({
            'id': 'count',
            'additions': 'sum',
            'deletions': 'sum',
            'changes': 'sum'
        }).reset_index().rename(columns={
            'id': 'commits'
        }).sort_values(by="commits", ascending=False)

        for user in self.getUsers():
            if len(commits[commits["user"] == user]) == 0:
                commits = commits.append(
                    {
                        "user": user,
                        "commits": 0,
                        "additions": 0,
                        "deletions": 0,
                        "changes": 0
                    },
                    ignore_index=True)

        return commits

    def getUsers(self):
        users = pd.concat([
            self.statsCollecter.getPRs()["assignee"],
            self.statsCollecter.getComments()["user"],
            self.statsCollecter.getCommits()["user"],
            self.statsCollecter.getIssues()["assignee"],
        ]).unique()
        return [u for u in users if u]

    def getPRs(self):
        return self.statsCollecter.getPRs()["id"].unique()

    def getCommentsByUserAndPR(self):
        comments = self.statsCollecter.getComments().groupby(
            ['user', 'pr']).agg({
                'id': 'count'
            }).reset_index().rename(columns={'id': 'comments'})

        for user in self.getUsers():
            for pr in self.getPRs():
                if len(comments[(comments["user"] == user) &
                                (comments["pr"] == pr)]) == 0:
                    comments = comments.append(
                        {
                            "pr": pr,
                            "user": user,
                            "comments": 0
                        },
                        ignore_index=True)
        return comments

    def getCommitsByUserAndPR(self):
        commits = self.statsCollecter.getCommits().groupby(['user', 'pr']).agg({
            'id': 'count',
            'additions': 'sum',
            'deletions': 'sum',
            'changes': 'sum'
        }).reset_index().rename(columns={'id': 'commits'})

        for user in self.getUsers():
            for pr in self.getPRs():
                if len(commits[(commits["user"] == user) &
                               (commits["pr"] == pr)]) == 0:
                    commits = commits.append(
                        {
                            "pr": pr,
                            "user": user,
                            "additions": 0,
                            "deletions": 0,
                            "changes": 0,
                            "commits": 0
                        },
                        ignore_index=True)
        return commits

    def getContributionsByUserAndPR(self):
        aggregated = self.getCommitsByUserAndPR().merge(
            self.getCommentsByUserAndPR(), how="left",
            on=["pr", "user"]).sort_values(by=["pr", "user"])

        aggregated["contributions"] = aggregated["commits"] + aggregated[
            "changes"] + aggregated["comments"]
        aggregated["contributed"] = aggregated["contributions"] > 0
        aggregated = aggregated.drop('contributions', 1)

        aggregated.drop(
            aggregated[aggregated['user'].astype(bool) == False].index,
            inplace=True)

        return aggregated

    def getContributionsByUser(self, contributionsByUserAndPR):
        return contributionsByUserAndPR.groupby(['user']).agg({
            'commits': 'sum',
            'changes': 'sum',
            'comments': 'sum',
            'contributed': 'sum'
        }).reset_index()

    def getIssues(self):
        issues = self.statsCollecter.getIssues()

        counted_issues = issues.copy()
        excluded_issues = issues.copy()

        if len(issues) == 0:
            return pd.DataFrame(columns=["label", "completed"]), issues

        counted_issues = counted_issues[counted_issues["labels"].apply(
            lambda labels: "feature" not in labels)]

        counted_issues["labels"] = counted_issues["labels"].apply(
            lambda labels: [
                label for label in labels
                if label in ["task", "exploration", "chore"]
            ])

        counted_issues["label_count"] = counted_issues["labels"].apply(
            lambda l: len(l))

        counted_issues = counted_issues[counted_issues["label_count"] == 1]

        counted_issues["label"] = counted_issues["labels"].apply(lambda i: i[0])
        issues = issues.drop('labels', 1)

        excluded_issues = excluded_issues[excluded_issues["number"].apply(
            lambda x: x not in counted_issues["number"].to_list())]

        if counted_issues.empty:
            counted_issues = pd.DataFrame(columns=["label", "completed"])
        else:
            counted_issues = counted_issues.groupby(['label']).agg({
                'number': 'count'
            }).rename(columns={
                'number': 'completed'
            }).reset_index().sort_values(by="label")

        return counted_issues, excluded_issues

    def getExpectedIssuesPerUser(self):
        days = (self.get_end() - self.get_start()).total_seconds() / 86400
        return 2 * days / 7

    def getTeamScore(self, users, issues):
        expected_issues = self.getExpectedIssuesPerUser() * len(users)
        if expected_issues == 0:
            return 0.
        return min(sum(issues["completed"]) / expected_issues, 1.5)

    def getFinalScores(self, effort, team_score):
        scores = pd.DataFrame()
        scores['user'] = effort['user']
        scores["score"] = round(effort["effort"] * team_score, 2)
        return scores
