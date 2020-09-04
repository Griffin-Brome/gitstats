import pandas as pd


class StatsCalculator:

    def __init__(self, statsCollector):
        self.statsCollecter = statsCollector

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
        return pd.concat([
            self.statsCollecter.getPRs()["assignee"],
            self.statsCollecter.getComments()["user"],
            self.statsCollecter.getCommits()["user"]
        ]).unique()

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

    def getEffortByUserFromContributions(self, contributions):
        aggregated = contributions.groupby(['user']).agg({
            'commits': 'sum',
            'changes': 'sum',
            'comments': 'sum',
            'contributed': 'sum'
        }).reset_index()
        aggregated["contributed"] = aggregated["contributed"] / aggregated[
            "contributed"].max() * 100
        aggregated["commits"] = aggregated["commits"] / aggregated[
            "commits"].max() * 100
        aggregated["changes"] = aggregated["changes"] / aggregated[
            "changes"].max() * 100
        aggregated["comments"] = aggregated["comments"] / aggregated[
            "comments"].max() * 100

        aggregated["effort"] = 5 * aggregated["contributed"] + 5 * aggregated[
            "commits"] + 3 * aggregated["changes"] + 2 * aggregated["comments"]
        aggregated["effort"] = aggregated["effort"] / aggregated["effort"].max(
        ) * 100
        return aggregated
