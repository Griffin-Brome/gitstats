from .fixtures import prs as prs_fixtures
from .fixtures import comments as comments_fixtures
from .fixtures import commits as commits_fixtures
from .fixtures import issues as issues_fixtures
from .mocks import MockStatsCollector
from gitstats import StatsCalculator


class TestStatsCalculator:

    def test_all_empty(self):
        collector = MockStatsCollector()
        calculator = StatsCalculator(collector)

        assert len(calculator.getUsers()) == 0
        assert len(calculator.getPRsByAssignee()) == 0
        assert len(calculator.getCommentsByUser()) == 0
        assert len(calculator.getCommentsByUserAndPR()) == 0
        assert len(calculator.getCommitsByUser()) == 0
        assert len(calculator.getCommitsByUserAndPR()) == 0
        assert len(calculator.getContributionsByUserAndPR()) == 0

    def test_prs_with_assignees(self):

        collector = MockStatsCollector(prs=prs_fixtures)
        calculator = StatsCalculator(collector)

        PRsByAssignee = calculator.getPRsByAssignee()
        assert len(calculator.getUsers()) == 2
        assert "Bob" in calculator.getUsers()
        assert "Joan" in calculator.getUsers()
        assert len(PRsByAssignee) == 2
        assert PRsByAssignee[PRsByAssignee["assignee"] ==
                             "Bob"]["assigned"].iloc[0] == 2
        assert PRsByAssignee[PRsByAssignee["assignee"] ==
                             "Joan"]["assigned"].iloc[0] == 1

        CommentsByUser = calculator.getCommentsByUser()
        assert len(calculator.getCommentsByUser()) == 2
        assert CommentsByUser[CommentsByUser["user"] ==
                              "Bob"]["comments"].iloc[0] == 0
        assert CommentsByUser[CommentsByUser["user"] ==
                              "Joan"]["comments"].iloc[0] == 0

        CommitsByUser = calculator.getCommitsByUser()
        assert len(CommitsByUser) == 2
        assert CommitsByUser[CommitsByUser["user"] ==
                             "Bob"]["commits"].iloc[0] == 0
        assert CommitsByUser[CommitsByUser["user"] ==
                             "Joan"]["commits"].iloc[0] == 0

        assert len(calculator.getCommentsByUserAndPR()) == 4
        assert len(calculator.getCommitsByUserAndPR()) == 4
        assert len(calculator.getContributionsByUserAndPR()) == 4

    def test_prs_with_comments(self):
        collector = MockStatsCollector(prs=prs_fixtures,
                                       comments=comments_fixtures)
        calculator = StatsCalculator(collector)

        PRsByAssignee = calculator.getPRsByAssignee()
        assert len(PRsByAssignee) == 2
        assert PRsByAssignee[PRsByAssignee["assignee"] ==
                             "Bob"]["assigned"].iloc[0] == 2
        assert PRsByAssignee[PRsByAssignee["assignee"] ==
                             "Joan"]["assigned"].iloc[0] == 1

        CommentsByUser = calculator.getCommentsByUser()
        assert len(CommentsByUser) == 2
        assert CommentsByUser[CommentsByUser["user"] ==
                              "Bob"]["comments"].iloc[0] == 1
        assert CommentsByUser[CommentsByUser["user"] ==
                              "Joan"]["comments"].iloc[0] == 0
        assert len(calculator.getCommitsByUser()) == 2
        assert len(calculator.getCommentsByUserAndPR()) == 4
        assert len(calculator.getCommitsByUserAndPR()) == 4
        assert len(calculator.getContributionsByUserAndPR()) == 4

    def test_prs_with_comments_and_commits(self):
        collector = MockStatsCollector(prs=prs_fixtures,
                                       comments=comments_fixtures,
                                       commits=commits_fixtures)
        calculator = StatsCalculator(collector)

        PRsByAssignee = calculator.getPRsByAssignee()
        assert len(PRsByAssignee) == 2
        assert PRsByAssignee[PRsByAssignee["assignee"] ==
                             "Bob"]["assigned"].iloc[0] == 2
        assert PRsByAssignee[PRsByAssignee["assignee"] ==
                             "Joan"]["assigned"].iloc[0] == 1

        CommentsByUser = calculator.getCommentsByUser()
        assert len(CommentsByUser) == 2
        assert CommentsByUser[CommentsByUser["user"] ==
                              "Bob"]["comments"].iloc[0] == 1
        assert CommentsByUser[CommentsByUser["user"] ==
                              "Joan"]["comments"].iloc[0] == 0
        CommitsByUser = calculator.getCommitsByUser()
        assert len(CommitsByUser) == 2
        assert CommitsByUser[CommitsByUser["user"] ==
                             "Bob"]["commits"].iloc[0] == 1
        assert CommitsByUser[CommitsByUser["user"] ==
                             "Joan"]["commits"].iloc[0] == 0
        assert len(calculator.getCommentsByUserAndPR()) == 4
        assert len(calculator.getCommitsByUserAndPR()) == 4

        ContributionsByUserAndPR = calculator.getContributionsByUserAndPR()
        assert len(ContributionsByUserAndPR) == 4
        bob_0 = ContributionsByUserAndPR[
            (ContributionsByUserAndPR["user"] == "Bob") &
            (ContributionsByUserAndPR["pr"] == 0)]
        bob_1 = ContributionsByUserAndPR[
            (ContributionsByUserAndPR["user"] == "Bob") &
            (ContributionsByUserAndPR["pr"] == 1)]
        joan_0 = ContributionsByUserAndPR[
            (ContributionsByUserAndPR["user"] == "Joan") &
            (ContributionsByUserAndPR["pr"] == 0)]
        joan_1 = ContributionsByUserAndPR[
            (ContributionsByUserAndPR["user"] == "Joan") &
            (ContributionsByUserAndPR["pr"] == 1)]
        assert bob_0["contributed"].iloc[0]
        assert not bob_1["contributed"].iloc[0]
        assert not joan_0["contributed"].iloc[0]
        assert not joan_1["contributed"].iloc[0]

    def test_effort_with_comments_and_commits(self):
        collector = MockStatsCollector(prs=prs_fixtures,
                                       comments=comments_fixtures,
                                       commits=commits_fixtures)
        calculator = StatsCalculator(collector)

        contributions = calculator.getContributionsByUserAndPR()

        effort = calculator.getEffortByUserFromContributions(contributions)
        assert effort[effort["user"] == "Bob"]["effort"].iloc[0] == 100.0
        assert effort[effort["user"] == "Joan"]["effort"].iloc[0] == 0.0

    def test_effort_with_only_comments(self):
        collector = MockStatsCollector(prs=prs_fixtures,
                                       comments=comments_fixtures)
        calculator = StatsCalculator(collector)

        contributions = calculator.getContributionsByUserAndPR()

        effort = calculator.getEffortByUserFromContributions(contributions)
        assert effort[effort["user"] == "Bob"]["effort"].iloc[0] == 100.0
        assert effort[effort["user"] == "Joan"]["effort"].iloc[0] == 0.0

    def test_get_start(self):
        collector = MockStatsCollector()
        calculator = StatsCalculator(collector)
        assert calculator.get_start() == collector.get_start()

    def test_get_end(self):
        collector = MockStatsCollector()
        calculator = StatsCalculator(collector)
        assert calculator.get_end() == collector.get_end()

    def test_issues(self):
        collector = MockStatsCollector(issues=issues_fixtures)
        calculator = StatsCalculator(collector)
        issues, excluded_issues = calculator.getIssues()
        assert len(issues) == 1
        assert len(excluded_issues) == 4

    def test_team_score_two_users_one_issue(self):
        users = ["Bob", "Joan"]

        collector = MockStatsCollector(issues=issues_fixtures)
        calculator = StatsCalculator(collector)
        issues, excluded_issues = calculator.getIssues()

        team_score = calculator.getTeamScore(users, issues)
        assert team_score == 0.25

    def test_team_score_one_user_one_issue(self):
        users = ["Bob"]

        collector = MockStatsCollector(issues=issues_fixtures)
        calculator = StatsCalculator(collector)
        issues, excluded_issues = calculator.getIssues()

        team_score = calculator.getTeamScore(users, issues)
        assert team_score == 0.50

    def test_team_score_no_users(self):
        users = []

        collector = MockStatsCollector()
        calculator = StatsCalculator(collector)
        issues, excluded_issues = calculator.getIssues()

        team_score = calculator.getTeamScore(users, issues)
        assert team_score == 0.00
