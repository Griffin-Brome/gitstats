from .mocks import MockRepository, MockPR, MockReview, MockCommit, MockComment, MockAuthor
from random import randint
from gitstats import StatsCollector, GithubAPIRepository
from datetime import datetime, timedelta


class TestStatsCollector:

    def test_no_prs(self):
        expected_prs = []
        repository = MockRepository(expected_prs)
        api_repository = GithubAPIRepository(repository)
        end = datetime.now() + timedelta(days=7)
        start = datetime.now() - timedelta(days=7)

        collector = StatsCollector(api_repository, start=start, end=end)

        assert len(collector.getPRs()) == 0
        assert len(collector.getReviews()) == 0
        assert len(collector.getComments()) == 0
        assert len(collector.getCommits()) == 0

    def test_collects_prs(self):
        expected_commits = []
        expected_reviews = []
        expected_review_comments = []
        expected_issue_comments = []
        expected_prs = []

        for i in range(0, 3):
            expected_commits.append(
                [MockCommit() for i in range(0, randint(0, 10))])
            expected_reviews.append(
                [MockReview() for i in range(0, randint(0, 10))])
            expected_review_comments.append(
                [MockComment() for i in range(0, randint(0, 10))])
            expected_issue_comments.append(
                [MockComment() for i in range(0, randint(0, 10))])
            expected_prs.append(
                MockPR(commits=expected_commits[i],
                       reviews=expected_reviews[i],
                       review_comments=expected_review_comments[i],
                       issue_comments=expected_issue_comments[i]))
        repository = MockRepository(expected_prs)
        api_repository = GithubAPIRepository(repository)

        end = datetime.now() + timedelta(days=7)
        start = datetime.now() - timedelta(days=7)

        collector = StatsCollector(api_repository, start=start, end=end)
        prs = collector.getPRs()
        reviews = collector.getReviews()
        comments = collector.getComments()
        commits = collector.getCommits()
        assert len(prs) == len(expected_prs)
        assert len(reviews) == sum([len(e) for e in expected_reviews])
        assert len(comments) == sum([len(e) for e in expected_issue_comments
                                    ]) + sum([
                                        len(e) for e in expected_review_comments
                                    ]) + sum([len(e) for e in expected_reviews])
        assert len(commits) == sum([len(e) for e in expected_commits])

    def test_excludes_user(self):

        users = ["Bob", "Jane", "TAJoe"]
        excluded_users = ["TAJoe"]
        expected_prs = []
        for pr_assignee in users:
            for commit_author in users:
                for review_commenter in users:
                    for issue_commenter in users:
                        commit = MockCommit(author=MockAuthor(
                            name=commit_author))
                        review_comment = MockComment(user=MockAuthor(
                            name=review_commenter))
                        issue_comment = MockComment(user=MockAuthor(
                            name=issue_commenter))

                        pr = MockPR(commits=[commit],
                                    reviews=[],
                                    review_comments=[review_comment],
                                    issue_comments=[issue_comment])
                        expected_prs.append(pr)
        repository = MockRepository(expected_prs)

        api_repository = GithubAPIRepository(repository)

        end = datetime.now() + timedelta(days=7)
        start = datetime.now() - timedelta(days=7)

        collector = StatsCollector(api_repository,
                                   start=start,
                                   end=end,
                                   excluded_users=excluded_users)
        prs = collector.getPRs()
        reviews = collector.getReviews()
        comments = collector.getComments()
        commits = collector.getCommits()
        assert len(prs) == 81
        assert len(reviews) == 0
        assert len(comments) == 108
        assert len(commits) == 54
