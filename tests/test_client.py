# -*- coding: utf-8 -*-
import re
import unittest
from flask import url_for
from app import create_app, db
from app.models import User, Role


class FlaskClientTestCase(unittest.TestCase):
    """使用flask内建的test_client测试视图函数"""
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        self.client = self.app.test_client(use_cookies=True)            # self.client是flask测试客户端对象

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_home_page(self):
        response = self.client.get(url_for('main.index'))   # get()方法得到一个flask的response对象 [GET]
        self.assertTrue(b'Stranger' in response.data)       # response.data得到的是bytesarray

    def test_register_and_login(self):
        # register a new account
        response = self.client.post(url_for('auth.register'), data={
            'email': 'john@example.com',  # 由于CSRF保护已在测试配置中禁用,因此无需和表单数据一起发送
            'username': 'john',
            'password': 'cat',
            'password2': 'cat'
        })                                                # 没有设置follow_redirects=True:返回302状态码,而不是重定向的url返回的响应
        self.assertTrue(response.status_code == 302)      # 检查:重定向(302);注册成功会重定向到登录页面

        # login with the new account
        response = self.client.post(url_for('auth.login'), data={
            'email': 'john@example.com',
            'password': 'cat'
        }, follow_redirects=True)                         # 有设置follow_redirects=True,返回重定向的url的响应,而不是302状态码
        self.assertTrue(re.search(b'Hello,\s+john!', response.data))
        self.assertTrue(b'You have not confirmed your account yet' in response.data)

        # send a confirmation token
        user = User.query.filter_by(email='john@example.com').first()
        token = user.generate_confirmation_token()
        response = self.client.get(url_for('auth.confirm', token=token),  # 访问token确认地址
                                   follow_redirects=True)
        self.assertTrue(b'You have confirmed your account' in response.data)

        # log out
        response = self.client.get(url_for('auth.logout'), follow_redirects=True)  # 有设置follow_redirects=True
        self.assertTrue(b'You have been logged out' in response.data)



