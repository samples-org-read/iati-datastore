import datetime
import inspect
from unittest import TestCase

from . import CSVTstMixin as _CSVTstMixin

from iatilib.test import factories as fac


from iatilib.frontend import serialize
from iatilib import codelists as cl


class TestCSVStream(TestCase):
    def test_stream(self):
        self.assertTrue(inspect.isgenerator(serialize.csv([])))

class CSVTstMixin(_CSVTstMixin):
    def serialize(self, data):
        return serialize.csv(data)


class TestCSVSerializer(CSVTstMixin, TestCase):
    def test_empty(self):
        data = self.process([])
        self.assertEquals(0, len(data))

    def test_len_one(self):
        data = self.process([fac.ActivityFactory.build()])
        self.assertEquals(1, len(data))

    def test_len_many(self):
        data = self.process([
            fac.ActivityFactory.build(),
            fac.ActivityFactory.build()
        ])
        self.assertEquals(2, len(data))

    def test_date_field(self):
        data = self.process([fac.ActivityFactory.build(
            start_planned=datetime.date(2012, 1, 1))
        ])
        self.assertField({"start-planned": "2012-01-01"}, data[0])

    def test_date_field_empty(self):
        data = self.process([fac.ActivityFactory.build(
            start_planned=None
        )])
        self.assertField({"start-planned": ""}, data[0])

    def test_quoting(self):
        data = self.process([fac.ActivityFactory.build(
            reporting_org__name=u"l,r"
        )])
        self.assertField({"reporting-org": "l,r"}, data[0])

    def test_unicode(self):
        data = self.process([fac.ActivityFactory.build(
            reporting_org__name=u"\u2603"
        )])
        self.assertField({"reporting-org": u"\u2603"}, data[0])

    def test_no_description(self):
        # Description is an optional thing
        data = self.process([fac.ActivityFactory.build(description="")])
        self.assertField({"description": ""}, data[0])


class TestCSVExample(CSVTstMixin, TestCase):
    # these tests are based around an example from IATI
    # https://docs.google.com/a/okfn.org/spreadsheet/ccc?key=0AqR8dXc6Ji4JdHJIWDJtaXhBV0IwOG56N0p1TE04V2c#gid=4

    def test_iati_identifier(self):
        data = self.process([
            fac.ActivityFactory.build(iati_identifier=u"GB-1-123")
        ])
        self.assertField({"iati-identifier": "GB-1-123"}, data[0])

    def test_title(self):
        data = self.process([
            fac.ActivityFactory.build(title=u"Project 123")
        ])
        self.assertField({"title": "Project 123"}, data[0])

    def test_description(self):
        data = self.process([fac.ActivityFactory.build(
            description=u"Description of Project 123")
        ])
        self.assertField({"description": "Description of Project 123"}, data[0])

    def test_end_actual(self):
        data = self.process([fac.ActivityFactory.build(
            end_actual=datetime.date(2012, 1, 1))
        ])
        self.assertField({"end-actual": "2012-01-01"}, data[0])

    def test_recepient_country_code(self):
        data = self.process([fac.ActivityFactory.build(
            recipient_country_percentages=[
                fac.CountryPercentageFactory.build(country=cl.Country.kenya),
                fac.CountryPercentageFactory.build(country=cl.Country.uganda),
            ]
        )])
        self.assertField({
            "recipient-country-code": "KE;UG"}, data[0])

    def test_recepient_country(self):
        data = self.process([fac.ActivityFactory.build(
            recipient_country_percentages=[
                fac.CountryPercentageFactory.build(country=cl.Country.kenya),
                fac.CountryPercentageFactory.build(country=cl.Country.uganda),
            ]
        )])
        self.assertField({"recipient-country": "Kenya;Uganda"}, data[0])

    def test_recepient_country_percentage(self):
        data = self.process([fac.ActivityFactory.build(
            recipient_country_percentages=[
                fac.CountryPercentageFactory.build(percentage=80),
                fac.CountryPercentageFactory.build(percentage=20),
            ]
        )])
        self.assertField({"recipient-country-percentage": "80;20"}, data[0])

    def test_sector_code(self):
        data = self.process([fac.ActivityFactory.build(
            sector_percentages=[
                fac.SectorPercentageFactory.build(
                    sector=cl.Sector.teacher_training),
                fac.SectorPercentageFactory.build(
                    sector=cl.Sector.primary_education),
            ]
        )])
        self.assertField({"sector-code": "11130;11220"}, data[0])

    def test_sector(self):
        data = self.process([fac.ActivityFactory.build(
            sector_percentages=[
                fac.SectorPercentageFactory.build(
                    sector=cl.Sector.teacher_training),
                fac.SectorPercentageFactory.build(
                    sector=cl.Sector.primary_education),
            ]
        )])
        self.assertField(
            {"sector": u"Teacher training;Primary education"},
            data[0])

    def test_sector_blank(self):
        data = self.process([fac.ActivityFactory.build(
            sector_percentages=[
                fac.SectorPercentageFactory.build(sector=None)
            ]
        )])
        self.assertField({"sector": u""}, data[0])

    def test_sector_percentage(self):
        data = self.process([fac.ActivityFactory.build(
            sector_percentages=[
                fac.SectorPercentageFactory.build(percentage=60),
                fac.SectorPercentageFactory.build(percentage=40)
            ]
        )])
        self.assertField({"sector-percentage": "60;40"}, data[0])

    def test_currency(self):
        data = self.process([fac.ActivityFactory.build(
            transactions=[
                fac.TransactionFactory.build(
                    value_currency=cl.Currency.us_dollar
                )
            ]
        )])
        self.assertField({"currency": "USD"}, data[0])

    def test_currency_mixed(self):
        data = self.process([fac.ActivityFactory.build(
            transactions=[
                fac.TransactionFactory.build(
                    value_currency=cl.Currency.us_dollar
                ),
                fac.TransactionFactory.build(
                    value_currency=cl.Currency.australian_dollar
                ),
            ]
        )])
        self.assertField({"currency": "!Mixed currency"}, data[0])

    def test_currency_missing(self):
        # If there is no default currency specified on the activity and
        # none on the transaction then we end up with a missing currency.
        data = self.process([fac.ActivityFactory.build(
            default_currency=None,
            transactions=[
                fac.TransactionFactory.build(
                    value_currency=None
                )
            ]
        )])
        self.assertField({"currency": ""}, data[0])

    def test_mixed_transation_types(self):
        data = self.process([fac.ActivityFactory.build(
            transactions=[
                fac.TransactionFactory.build(
                    type=cl.TransactionType.disbursement,
                    value_amount=1,
                ),
                fac.TransactionFactory.build(
                    type=cl.TransactionType.expenditure,
                    value_amount=2
                ),
            ]
        )])
        self.assertField({"currency": "USD"}, data[0])
        self.assertField({"total-Disbursement": "1"}, data[0])
        self.assertField({"total-Expenditure": "2"}, data[0])


class ActivityExample(object):
    def example(self):
        activity = fac.ActivityFactory.build(
            iati_identifier=u"GB-1-123",
            title=u"Project 123",
            description=u"Desc 123",
            recipient_country_percentages=[
                fac.CountryPercentageFactory.build(
                    country=cl.Country.kenya,
                    percentage=80
                ),
                fac.CountryPercentageFactory.build(
                    country=cl.Country.uganda,
                    percentage=20
                ),
            ],
            sector_percentages=[
                fac.SectorPercentageFactory.build(
                    sector=cl.Sector.teacher_training,
                    percentage=60),
                fac.SectorPercentageFactory.build(
                    sector=cl.Sector.primary_education,
                    percentage=40),
            ],
            transactions=[
                fac.TransactionFactory.build(
                    value_currency=cl.Currency.pound_sterling,
                    type=cl.TransactionType.commitment,
                    value_amount=130000
                )
            ]
        )
        return activity


class TestActivityByCountry(CSVTstMixin, ActivityExample, TestCase):
    def serialize(self, data):
        return serialize.csv_activity_by_country(data)

    def example(self):
        activity = super(TestActivityByCountry, self).example()
        return [
            (activity, activity.recipient_country_percentages[0]),
            (activity, activity.recipient_country_percentages[1])
        ]


    def test_no_rows(self):
        data = self.process(self.example())
        self.assertEquals(2, len(data))

    def test_column_list(self):
        data = self.process(self.example())
        cols = [
            "recipient-country-code",
            "recipient-country",
            "recipient-country-percentage",
            "iati-identifier",
            "title",
            "description",
            "sector-code",
            "sector",
            "sector-percentage",
            "currency",
            "total-Commitment",
            "total-Disbursement",
            "total-Expenditure",
            "total-Incoming Funds",
            "total-Interest Repayment",
            "total-Loan Repayment",
            "total-Reimbursement"
        ]
        for col in cols:
            self.assertIn(col, data[0].keys(), msg="Missing col %s" % col)

    def test_country_code_0(self):
        data = self.process(self.example())
        self.assertField({"recipient-country-code": u"KE"}, data[0])

    def test_country_code_1(self):
        data = self.process(self.example())
        self.assertField({"recipient-country-code": u"UG"}, data[1])

    def test_country(self):
        data = self.process(self.example())
        self.assertField({"recipient-country": u"Kenya"}, data[0])

    def test_recipient_country_percentage_0(self):
        data = self.process(self.example())
        self.assertField({"recipient-country-percentage": u"80"}, data[0])

    def test_recipient_country_percentage_1(self):
        data = self.process(self.example())
        self.assertField({"recipient-country-percentage": u"20"}, data[1])

    def test_identifier(self):
        data = self.process(self.example())
        self.assertField({"iati-identifier": u"GB-1-123"}, data[0])

    def test_title(self):
        data = self.process(self.example())
        self.assertField({"title": u"Project 123"}, data[0])

    def test_description(self):
        data = self.process(self.example())
        self.assertField({"description": u"Desc 123"}, data[0])

    def test_sector_code_0(self):
        data = self.process(self.example())
        self.assertField({"sector-code": u"11130;11220"}, data[0])

    def test_sector_code_1(self):
        data = self.process(self.example())
        self.assertField({"sector-code": u"11130;11220"}, data[1])

    def test_sector(self):
        data = self.process(self.example())
        self.assertField(
            {"sector": u"Teacher training;Primary education"},
            data[1])

    def test_sector_percentage(self):
        data = self.process(self.example())
        self.assertField({"sector-percentage": u"60;40"}, data[1])

    def test_currency(self):
        data = self.process(self.example())
        self.assertField({"currency": u"GBP"}, data[1])

    def test_total_commitment(self):
        data = self.process(self.example())
        self.assertField({"total-Commitment": u"130000"}, data[0])


class TestActivityBySector(CSVTstMixin, ActivityExample, TestCase):
    def serialize(self, data):
        return serialize.csv_activity_by_sector(data)

    def example(self):
        activity = super(TestActivityBySector, self).example()
        return [
            (activity, activity.sector_percentages[0]),
            (activity, activity.sector_percentages[1])
        ]

    def test_no_rows(self):
        data = self.process(self.example())
        self.assertEquals(2, len(data))

    def test_sector_code_0(self):
        data = self.process(self.example())
        self.assertField({"sector-code": u"11130"}, data[0])

    def test_sector_code_1(self):
        data = self.process(self.example())
        self.assertField({"sector-code": u"11220"}, data[1])

    def test_sector_0(self):
        data = self.process(self.example())
        self.assertField({"sector": u"Teacher Training"}, data[0])

    def test_sector_1(self):
        data = self.process(self.example())
        self.assertField({"sector": u"Primary Education"}, data[1])

    def test_sector_percentage_0(self):
        data = self.process(self.example())
        self.assertField({"sector-percentage": u"60"}, data[0])

    def test_sector_percentage_1(self):
        data = self.process(self.example())
        self.assertField({"sector-percentage": u"40"}, data[1])

    def test_identifier(self):
        data = self.process(self.example())
        self.assertField({"iati-identifier": u"GB-1-123"}, data[0])





class TotalFieldMixin(object):
    # There are six total fields that behave identicaly
    def test_total(self):
        data = self.process([fac.ActivityFactory.build(
            transactions=[
                fac.TransactionFactory.build(
                    type=self.transaction_type,
                    value_amount=130000
                ),
            ]
        )])
        self.assertField({self.csv_field: "130000"}, data[0])

    def test_many_trans(self):
        data = self.process([fac.ActivityFactory.build(
            transactions=[
                fac.TransactionFactory.build(
                    type=self.transaction_type,
                    value_amount=2
                ),
                fac.TransactionFactory.build(
                    type=self.transaction_type,
                    value_amount=1
                ),
            ]
        )])
        self.assertField({self.csv_field: "3"}, data[0])

    def test_many_currencies(self):
        data = self.process([fac.ActivityFactory.build(
            transactions=[
                fac.TransactionFactory.build(
                    type=self.transaction_type,
                    value_amount=2,
                    value_currency=cl.Currency.us_dollar,
                ),
                fac.TransactionFactory.build(
                    type=self.transaction_type,
                    value_amount=1,
                    value_currency=cl.Currency.australian_dollar
                ),
            ]
        )])
        self.assertField({self.csv_field: "!Mixed currency"}, data[0])


class TestTotalDisbursement(CSVTstMixin, TotalFieldMixin, TestCase):
    transaction_type = cl.TransactionType.disbursement
    transaction_code = "D"
    csv_field = "total-Disbursement"


class TestTotalExpenditure(CSVTstMixin, TotalFieldMixin, TestCase):
    transaction_type = cl.TransactionType.expenditure
    csv_field = "total-Expenditure"


class TestTotalIncomingFunds(CSVTstMixin, TotalFieldMixin, TestCase):
    transaction_type = cl.TransactionType.incoming_funds
    csv_field = "total-Incoming Funds"


class TestTotalInterestRepayment(CSVTstMixin, TotalFieldMixin, TestCase):
    transaction_type = cl.TransactionType.interest_repayment
    csv_field = "total-Interest Repayment"


class TestTotalLoanRepayment(CSVTstMixin, TotalFieldMixin, TestCase):
    transaction_type = cl.TransactionType.loan_repayment
    csv_field = "total-Loan Repayment"


class TestTotalReimbursement(CSVTstMixin, TotalFieldMixin, TestCase):
    transaction_type = cl.TransactionType.reimbursement
    csv_field = "total-Reimbursement"

