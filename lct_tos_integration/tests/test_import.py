from openerp.tests.common import TransactionCase
from openerp.osv import osv
import os
from ftplib import FTP

class TestImport(TransactionCase):

    def setUp(self):
        super(TestImport, self).setUp()
        self.ftp_config_model = self.registry('ftp.config')
        self.invoice_model = self.registry('account.invoice')
        self.partner_model = self.registry('res.partner')
        self.import_data_model = self.registry('lct.tos.import.data')
        cr, uid = self.cr, self.uid
        config_ids = self.ftp_config_model.search(cr, uid, [])
        self.ftp_config_model.unlink(cr, uid, config_ids)
        self.config = config = dict(
            name="Config",
            active=True,
            addr='192.168.0.11',
            user='openerp',
            psswd='Azerty01',
            inbound_path='test_inbound/transfer_complete',
            outbound_path='test_outbound/transfer_complete'
        )
        self.config_id = self.ftp_config_model.create(cr, uid, config)

    def test_only_one_active(self):
        cr, uid = self.cr, self.uid
        config2 = dict(
            name="Config2",
            active=True,
            addr='Address',
            user='user',
            psswd='password',
            inbound_path='in_path',
            outbound_path='out_path'
            )
        with self.assertRaises(Exception,
                msg='Creating a second active config should raise an error'):
            self.ftp_config_model.create(cr, uid, config2)

    def _prepare_import(self):
        config = self.config
        ftp = FTP(host=config['addr'], user=config['user'], passwd=config['psswd'])
        ftp.cwd(config['outbound_path'])
        for outbound_file in ftp.nlst():
            if outbound_file != "done":
                try:
                    ftp.delete(outbound_file)
                except:
                    ftp.rmd(outbound_file)
        xml_dirs = ['APP_XML_files']
        local_path_path = os.path.join(__file__.split(__file__.split(os.sep)[-1])[0], 'xml_files')
        for xml_dir in xml_dirs:
            local_path = os.path.join(local_path_path, xml_dir)
            for xml_file in os.listdir(local_path):
                xml_abs_file = os.path.join(local_path, xml_file)
                ftp.storlines(''.join(['STOR ', xml_file]), open(xml_abs_file))

    def test_import(self):
        cr, uid = self.cr, self.uid
        ftp_config_model = self.ftp_config_model
        invoice_model, import_data_model = self.invoice_model, self.import_data_model
        self._prepare_import()
        inv_ids = invoice_model.search(cr, uid, ['|',('type2','=','vessel'),('type2','=','appointment')])
        if inv_ids:
            invoice_model.unlink(cr, uid, inv_ids)
        data_ids = import_data_model.search(cr, uid, [])
        if data_ids:
            import_data_model.unlink(cr, uid, data_ids)
        ftp_config_model.button_import_ftp_data(cr, uid, [self.config_id])
        vessel_ids = invoice_model.search(cr, uid, [('type2','=','vessel')])
        appoint_ids = invoice_model.search(cr, uid, [('type2','=','appointment')])

