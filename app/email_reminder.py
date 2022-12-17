# -*- coding: utf-8 -*-
"""
发送邮件的模块程序
"""
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
import cv2 


def send_email_remind(email_cfg_info_object, frame):
    """
    发送邮件函数，可以发送监控信息（个数、人体的坐标信息），并附带当前抓拍的图片（为了节省传输时间、硬件资源，采用缩略图）

    :param email_cfg_info_object: EMAIL_CONFIG_INO 类对象，该 EMAIL_CONFIG_INO 在 read_cfg_yml.py 中定义
    :param frame: numpy.ndarray类型
    :return: None
    """
    import time 
    begin_time = time.time()

    # 通过第三方 SMTP 服务来发送邮件
    mail_host = "smtp.126.com"  #设置服务器，这里以126服务器为例

    mail_user = email_cfg_info_object.email_sender_account_usr    # 用户名，需要在 app/config/params.yml 输入自己的实际用户名
    mail_pass = email_cfg_info_object.emial_sender_account_pwd   # 密码，需要在 app/config/params.yml 输入自己的实际密码    
    
    sender = email_cfg_info_object.email_sender_account_usr # 注意：[sender] must be same with [mai_user]
    # receivers = [email_cfg_info_object.email_receiver_account_usr]  # 接收邮件，可设置为你的QQ邮箱或者其他实际邮箱，也需要在 app/config/params.yml 配置
    receiver = [email_cfg_info_object.email_receiver_account_usr]  # 接收邮件，可设置为你的QQ邮箱或者其他实际邮箱，也需要在 app/config/params.yml 配置


    assert mail_user == sender, "two mail address must be same!!!"

    # 不带图片发送邮件的方式
    # email_content = email_cfg_info_object.email_content_template
    # print ('email content real time: {}'.format(email_content))
    # print ('type of img:', type(frame))
    # message = MIMEText('{}'.format(str(email_content)), 'plain', 'utf-8')
    # message['From'] = Header("william@wieye.cn", 'utf-8')  # 邮件里看到的发件人信息，自己可以随意写，这里先默认为：william@wieye.cn 
    # message['To'] =  Header("william@wieye.cn", 'utf-8')
    
    # subject =  email_cfg_info_object.email_subject # 邮件的主题，也需要在 config/email.yml 配置
    # message['Subject'] = Header(subject, 'utf-8')

    # 带图片发送邮件的方式
    msgRoot = MIMEMultipart('related')
    msgRoot['From'] = Header("william@wieye.cn", 'utf-8')  # 邮件里看到的发件人信息，自己可以随意写，这里先默认为：william@wieye.cn 
    msgRoot['To'] =  Header("william@wieye.cn", 'utf-8')

    subject = email_cfg_info_object.email_subject # 邮件的主题，也需要在 config/email.yml 配置
    msgRoot['Subject'] = Header(subject, 'utf-8')
    
    msgAlternative = MIMEMultipart('alternative') 
    mail_msg = """
    <p>{}</p>
    <p>最新核酸队伍现场图片：</p>
    <p><img src="cid:image"></p>
    """.format(email_cfg_info_object.email_content_template)

    msgAlternative.attach(MIMEText(mail_msg, 'html', 'utf-8'))
    msgRoot.attach(msgAlternative)

    img_info = MIMEImage(cv2.imencode('.jpg', frame)[1].tobytes())
    img_info.add_header('Content-ID', '<image>')
    msgRoot.attach(img_info)

    try:
        smtpObj = smtplib.SMTP() 
        print ('conneting to connect email server...')
        smtpObj.connect(mail_host, 25)    # 25 为 SMTP 端口号，网易邮件配置信息参考：http://help.163.com/09/0219/10/52GOPOND007536NI.html
        print ('begain to login')
        smtpObj.login(mail_user, mail_pass)  
        print ('login over!')
        smtpObj.sendmail(sender, receiver, msgRoot.as_string())
        print ("send email ok!!!")
    except smtplib.SMTPException:
        print ("Error: can not send email!!! pls check email account and pwd!!!")

    end_time = time.time()
    print ('send email cost: {} ms'.format(1000*(end_time-begin_time)))