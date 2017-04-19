from mock import MagicMock, patch
import datetime

from opal.core.test import OpalTestCase
from opal.core.search import search_query


class SearchQueryFieldTestCase(OpalTestCase):
    def setUp(self, *args, **kwargs):
        class SomeSearchQueryField(search_query.SearchQueryField):
            lookup_list = "some_list"
            enum = [1, 2, 3]
            description = "its a custom field"
            display_name = "custom field you know"
            field_type = "string"
            slug = "some_slug"
        self.custom_field = SomeSearchQueryField()
        super(SearchQueryFieldTestCase, self).setUp(*args, **kwargs)

    def test_slug_if_slug_provided(self):
        self.assertEqual(self.custom_field.get_slug(), "some_slug")

    def test_slug_if_slug_not_provided(self):
        class SomeOtherSearchQueryField(search_query.SearchQueryField):
            lookuplist = "some_list"
            enum = [1, 2, 3]
            description = "its a custom field"
            display_name = "custom field you know"
        self.assertEqual(
            SomeOtherSearchQueryField().get_slug(), "customfieldyouknow"
        )

    def test_display_name(self):
        self.assertEqual(
            self.custom_field.get_display_name(),
            "custom field you know"
        )

    def test_display_name_not_set(self):
        class SomeFlawedSearchQueryField(search_query.SearchQueryField):
            pass

        with self.assertRaises(ValueError) as va:
            SomeFlawedSearchQueryField().get_slug()

        self.assertIn("Must set display_name for", str(va.exception))

    def test_query(self):
        with self.assertRaises(NotImplementedError) as nie:
            self.custom_field.query("some query")

        self.assertEqual("please implement a query", str(nie.exception))

    def test_to_dict(self):
        expected = dict(
            lookup_list="some_list",
            enum=[1, 2, 3],
            description="its a custom field",
            name="some_slug",
            title='custom field you know',
            type="string"
        )
        self.assertEqual(
            self.custom_field.to_dict(),
            expected
        )


class SearchQueryTestCase(OpalTestCase):
    def test_get(self):
        some_mock_query = MagicMock()
        with patch.object(search_query.SearchQuery, "list") as get_list:
            get_list.return_value = [some_mock_query]
            some_mock_query.get_slug.return_value = "tree"
            result = search_query.SearchQuery.get("tree")
            self.assertEqual(result, some_mock_query)

    def test_get_if_missing(self):
        some_mock_query = MagicMock()
        with patch.object(search_query.SearchQuery, "list") as get_list:
            get_list.return_value = [some_mock_query]
            some_mock_query.get_slug.return_value = "tree"
            result = search_query.SearchQuery.get("onion")
            self.assertIsNone(result)

    def test_get_fields(self):
        self.assertEqual(search_query.SearchQuery().get_fields(), [])

    def test_query(self):
        some_mock_query = MagicMock()

        with patch.object(
            search_query.SearchQuery, "get_fields"
        ) as get_fields:
            get_fields.return_value = [some_mock_query]
            some_mock_query().get_slug.return_value = "tree"
            some_mock_query().query.return_value = "some_result"
            query = dict(field="tree")
            result = search_query.SearchQuery().query(query)
            self.assertEqual(result, "some_result")
            some_mock_query().query.assert_called_once_with(query)


class EpisodeQueryTestCase(OpalTestCase):
    def setUp(self, *args, **kwargs):
        super(EpisodeQueryTestCase, self).setUp(*args, **kwargs)
        _, self.episode = self.new_patient_and_episode_please()
        self.episode.date_of_admission = datetime.date(2017, 1, 1)
        self.episode.discharge_date = datetime.date(2017, 1, 5)
        self.episode.save()
        self.episode_query = search_query.EpisodeQuery()

    def test_episode_end_start(self):
        query_end = dict(
            queryType="Before",
            query="1/8/2017",
            field="end"
        )
        self.assertEqual(
            list(self.episode_query.query(query_end))[0], self.episode
        )

    def test_episode_end_after(self):
        query_end = dict(
            queryType="After",
            query="1/8/2015",
            field="end"
        )
        self.assertEqual(
            list(self.episode_query.query(query_end))[0], self.episode
        )

    def test_episode_end_not_found(self):
        query_end = dict(
            queryType="Before",
            query="1/8/2010",
            field="end"
        )
        self.assertEqual(
            list(self.episode_query.query(query_end)), []
        )

    def test_episode_end_wrong_query_param(self):
        query_end = dict(
            queryType="asdfsadf",
            query="1/8/2010",
            field="end"
        )
        with self.assertRaises(search_query.SearchException):
            self.episode_query.query(query_end)

    def test_episode_start_before(self):
        query_end = dict(
            queryType="Before",
            query="1/8/2017",
            field="start"
        )
        self.assertEqual(
            list(self.episode_query.query(query_end))[0], self.episode
        )

    def test_episode_start_after(self):
        query_end = dict(
            queryType="After",
            query="1/8/2015",
            field="start"
        )
        self.assertEqual(
            list(self.episode_query.query(query_end))[0], self.episode
        )

    def test_episode_start_not_found(self):
        query_end = dict(
            queryType="Before",
            query="1/8/2011",
            field="start"
        )
        self.assertEqual(
            list(self.episode_query.query(query_end)), []
        )

    def test_episode_start_wrong_query_param(self):
        query_end = dict(
            queryType="asdfsadf",
            query="1/8/2010",
            field="start"
        )
        with self.assertRaises(search_query.SearchException):
            self.episode_query.query(query_end)
