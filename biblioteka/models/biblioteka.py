from odoo import api, fields, models
from odoo import tools, _
from odoo.exceptions import ValidationError,UserError
from odoo.modules.module import get_module_resource
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time


class Biblioteka(models.Model):
    _name = "biblioteka.biblioteka"
    _description="Biblioteka"

    name = fields.Char(string="Name", required=True)
    status = fields.Char(string="Status")
    date_aprovimi = fields.Date(string='Start Date', default=datetime.today())
    date_dorezimi = fields.Date(string='End Date')

    arsye_vonese = fields.Text(string="Late explanation")
    lexues_id = fields.Many2one('biblioteka.lexues', string="ID_User")
    liber_id = fields.Many2one('biblioteka.librat', string="ID_Book")


class Librat(models.Model):
    _name = "biblioteka.librat"
    _description = "Library"

    title = fields.Char(string="Title", required=True)
    author = fields.Many2one('biblioteka.author',  string="Author", required=True)
    sasi_fizike = fields.Integer(string="Quantity", default='20')
    sasi_gjendje = fields.Integer(string="State", compute='rezervimi')
    informacion = fields.Char(string="About")
    disponueshmeria = fields.Boolean(string="Disponible", default='_compute_sasi')
    rezervuar = fields.Char(string="Book Reservation")
    rezervuar = fields.Selection([('available', 'Available'), ('non-available', 'Non-Available')],
                                 string="Book Reservation", default='available')
    liber_id = fields.Many2one('biblioteka.biblioteka', string="ID")

    @api.onchange('disponueshmeria')
    def _compute_sasi(self):
        if self.sasi_gjendje<1:
            self.disponueshmeria=False
        self.disponueshmeria=True

    @api.depends('rezervuar')
    def rezervimi(self):
        if self.rezervuar=='available':
            self.sasi_gjendje=self.sasi_fizike-1
            self.sasi_fizike=self.sasi_gjendje


class LibraryBookReturnday(models.Model):
    _name = 'biblioteka.returnday'
    _description = "Library Collection"
    _rec_name = 'day'

    day = fields.Integer(string="Days", required=True, help="It show the no of day/s for returning book")
    code = fields.Char(string="Code")
    fine_amt = fields.Float(string="Fine Amount", required=True, help="Fine amount after due of book return date")


class Lexues(models.Model):
    _name = "biblioteka.lexues"
    _description = "Lexues"

    lexues_id = fields.Many2one('biblioteka.biblioteka', string="ID_User")
    name = fields.Char(string="Name", required=True)
    mbiemer = fields.Char(string="Surname", required=True)
    mosha = fields.Date(string="Age", required=True)
    informacion = fields.Char(string="Information")
    date_regjistrimi = fields.Datetime(string="Date Regjistrimi")
    date_skadence = fields.Date(string="Riregjistrim", default="01/01/2019")
    dita = fields.Datetime(string="Data sot:", default=datetime.today())
    date_cregjistrimi = fields.Date(string="Date Cregjistrimi", default=time.strftime('%Y-01-31'))
    date_perjashtimi = fields.Date(string="Date Perjashtimi", default=time.strftime('%Y-01-01'))
    status = fields.Selection(
        [('draft', 'Draft'), ('regjistruar', 'Regjistruar'), ('perjashtuar', 'Perjashtuar'), ('skaduar', 'Skaduar'),
         ('cregjistruar', 'Cregjistruar')], default='draft')
    vlefshmeria = fields.Datetime(string="Vlefshmeria", compute='_compute_retunr_date')
    afat_riregjistrimi = fields.Date(string="Skadenca", compute='_compute_afati_i_ri')

    @api.depends('date_regjistrimi', 'vlefshmeria')
    def _compute_retunr_date(self):
        for record in self:
            if record.date_regjistrimi and record.vlefshmeria:
                ret_date = (datetime.strptime(record.date_regjistrimi, "%Y-%m-%d %H:%M:%S") + relativedelta(
                    days=record.vlefshmeria.day or 0.0))
                record.vlefshmeria = ret_date

    @api.depends('date_regjistrimi')
    def _compute_afati_i_ri(self):
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        self.afat_riregjistrimi = datetime.strptime(self.date_regjistrimi, DATETIME_FORMAT) + timedelta(days=30)

    @api.multi
    def _check_date(self):
        for lexues in self:
            # raise UserError(_("%s,%s,%s")%(  lexues.vlefshmeria ,fields.Datetime.now(),lexues.vlefshmeria < fields.Datetime.now()))
            if lexues.afat_riregjistrimi < fields.Datetime.now():
                return lexues.write({'status': 'skaduar'})
            return True

    @api.multi
    def draft_progressbar(self):
        self.ensure_one()
        self.write({
            'status': 'draft',
        })

    @api.multi
    def regjistruar_progressbar(self):
        self.ensure_one()
        self.write({
            'status': 'regjistruar',
        })

    @api.multi
    def skaduar_progressbar(self):
        self.ensure_one()
        self.write({
            'status': 'skaduar',
        })

    @api.multi
    def perjashtuar_progressbar(self):
        self.ensure_one()
        self.write({
            'status': 'perjashtuar',
        })

    @api.multi
    def cregjistruar_progressbar(self):
        self.ensure_one()
        self.write({
            'status': 'cregjistruar',
        })

    @api.multi
    def riregjistruar_progressbar(self):
        self.ensure_one()
        self.write({
            'status': 'riregjistruar',
        })


class Author(models.Model):
    _name = 'biblioteka.author'
    _description = "Author"

    name = fields.Char(string="Name", required=True, select=True)
    born_date = fields.Date(string="Date of Birth")
    death_date = fields.Date(string="Date of Death")
    note = fields.Text(string="Information")
