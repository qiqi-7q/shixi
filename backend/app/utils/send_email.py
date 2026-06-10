from app.core.config import settings

from fastapi_mail import FastMail, MessageSchema, MessageType,ConnectionConfig
from pydantic import EmailStr

conf = ConnectionConfig(
    # 发件人邮箱
    MAIL_USERNAME=settings.MAIL_USERNAME,
    # 邮箱授权码（不是登录密码！）
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    # 发件人邮箱
    MAIL_FROM=settings.MAIL_FROM,
    # 发件人名称
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    # SMTP 服务器地址
    MAIL_SERVER=settings.MAIL_SERVER,  # QQ邮箱用这个
    # MAIL_SERVER="smtp.163.com",  # 163邮箱用这个
    # SMTP 端口（465 是 SSL 安全端口，几乎通用）
    MAIL_PORT=settings.MAIL_PORT,
    # 使用 SSL 加密
    MAIL_SSL_TLS=True,
    MAIL_STARTTLS=False,
    # 验证发件人
    VALIDATE_CERTS=False
)


# 3. 发送普通文本邮件接口
async def send_text_email(
    to_email: EmailStr,  # 收件人邮箱
    subject: str = "测试",  # 邮件标题
    body: str = "da"  # 邮件内容
):
    subject = "忘记密码邮件"

    # 构造邮件消息
    message = MessageSchema(
        subject=subject,
        recipients=[to_email],  # 收件人列表
        body=body,
        subtype=MessageType.plain  # 纯文本
    )

    # 发送邮件
    fm = FastMail(conf)
    await fm.send_message(message)
    return {"code":200 , "msg": "邮件发送成功！","data":None}