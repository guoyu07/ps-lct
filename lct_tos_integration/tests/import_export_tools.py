from StringIO import StringIO
from lxml import etree as ET
import os

def upload_file(ftp, f, file_name):
    f.seek(0)
    result = ftp.storbinary(''.join(['STOR ', file_name]), f)
    return 199 < int(result[0:3]) < 300

def set_appointment_customer(xml_file, partner_id):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    for appoint in root.findall('appointment'):
        appoint.find('customer_id').text = str(partner_id)
    f = StringIO()
    f.write(ET.tostring(tree, pretty_print=True))
    return f

def set_vbilling_customer(xml_file, partner_id):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    for vbilling in root.findall('vbilling'):
        partner_id = str(partner_id)
        vbilling.find('customer_id').text = partner_id
        lines = vbilling.find('lines')
        for line in lines.findall('line'):
            line.find('container_customer_id').text = partner_id
    f = StringIO()
    f.write(ET.tostring(tree, pretty_print=True))
    return f

def set_dockage_customer(xml_file, partner_id):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    for dockage in root.findall('call'):
        dockage.find('customer_id').text = str(partner_id)
    f = StringIO()
    f.write(ET.tostring(tree, pretty_print=True))
    return f

def purge_ftp(ftp, path='', omit=[]):
    omit.extend(['.', '..'])
    files = ftp.nlst(path)
    if path:
        files = [f.rstrip(os.sep).split(os.sep)[-1] for f in files]
    files = [f for f in files if f not in omit]
    for f in files:
        f = os.path.join(path, f)
        try:
            ftp.delete(f)
        except:
            ftp.rmd(f)

def ls(ftp):
    return [filename for filename in ftp.nlst() if filename not in ['.', '..']]
