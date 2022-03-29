#! /usr/bin/python

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import colors


class HeaderVuln(object):

    def __init__(self, url):
        self.url = url

    def get_response(self):
        try:
            resp = requests.get(self.url)
            return resp
        except _:
            colors.error('Error in network connection')

    def gather_header(self):
        try:
            r = self.get_response()
            headers_dict = r.headers
            colors.info('Header Details')
            for key, value in headers_dict.items():
                colors.success(' {} : {} '.format(key, value))
            return headers_dict
        except Exception as e:
            colors.error(e)

    def find_insecure_headers(self):
        headers_dict = self.gather_header()

        if headers_dict:
            colors.info('Finding vulnerabilities')

            try:
                xssprotect = headers_dict['X-XSS-Protection']
                if xssprotect != '1; mode=block':
                    colors.error('X-XSS-Protection not set propely')
                else:
                    colors.success('X-XSS-Protection set properly.')
            except _:
                colors.info('Escaping')

            try:
                contenttype = headers_dict['X-Content-Type-Options']
                if contenttype != 'nosniff':
                    colors.error('X-Content-Type-Options not set properly.')
            except _:
                colors.info('Escaping')

            try:
                hsts = headers_dict['Strict-Transport-Security']
            except _:
                colors.error('HSTS not set properly.')

            try:
                csp = headers_dict['Content-Security-Policy']
                colors.success('CSP set properly.')
            except _:
                colors.error('CSP missing')

            try:
                xframe = headers_dict['x-frame-options']
                colors.success('Likely to be safe from X-Frame')
            except _:
                colors.error('X-Frame Missing')

    def insecure_cookies(self):
        response = self.get_response()
        cookies = response.cookies

        colors.info('Testing Insecure Cookies')
        cookie_data = []

        for cookie in cookies:
            colors.success('Name : {}'.format(cookie.name))
            colors.success('Value : {}'.format(cookie.value))
            cookie_data.append('Name : {}'.format(cookie.name))
            cookie_data.append('Value : {}'.format(cookie.value))

            if not cookie.secure:
                cookie.secure = 'True'
            else:
                cookie.secure = 'False'

            if 'httponly' in cookie._rest.keys():
                cookie.httponly = 'True'
            else:
                cookie.httponly = 'False'

            if cookie.domain_initial_dot:
                cookie.domain_initial_dot = 'True'
            else:
                cookie.domain_initial_dot = 'False'

            colors.success('Cookie secure : {}'.format(cookie.secure))
            colors.success('Cookie HTTP Only : {}'.format(cookie.httponly))
            colors.success('Cookie domain initial dot : {}'
                           .format(cookie.domain_initial_dot))
            print('\n')
            cookie_data.append('Cookie secure : {}'.format(cookie.secure))
            cookie_data.append('Cookie HTTP Only : {}'.format(cookie.httponly))
            cookie_data.append('Cookie domain initial dot : {}'
                               .format(cookie.domain_initial_dot) + '\n')

        return cookie_data

    def test_http_methods(self):
        modes_list = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'TRACE',
                      'TEST']

        colors.info('Testing HTTP methods')
        method_data = []

        for mode in modes_list:
            r = requests.request(mode, self.url)
            colors.success(' {} {} {}'.format(mode, r.status_code, r.reason))
            method_data.append(mode)
            method_data.append(r.status_code)
            method_data.append(r.reason)

            if mode == 'TRACE' and 'TRACE / HTTP/1.1' in r.text:
                colors.info('Possible Cross Site Tracing vulnerability found')

        return method_data
