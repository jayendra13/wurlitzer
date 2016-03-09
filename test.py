# coding: utf-8
from __future__ import print_function

import io
import mock

from wurlitzer import (
    libc, capture, STDOUT, PIPE, c_stderr_p, c_stdout_p,
    redirect_to_sys, redirect_everything_to_sys,
    stop_redirecting_everything,
)

def printf(msg):
    """Call C printf"""
    libc.printf((msg + '\n').encode('utf8'))

def printf_err(msg):
    """Cal C fprintf on stderr"""
    libc.fprintf(c_stderr_p, (msg + '\n').encode('utf8'))

def test_capture_pipes():
    with capture(stdout=PIPE, stderr=PIPE) as (stdout, stderr):
        printf(u"Hellø")
        printf_err(u"Hi, stdérr")
    
    assert stdout.read() == u"Hellø\n"
    assert stderr.read() == u"Hi, stdérr\n"

def test_capture_forward():
    stdout = io.StringIO()
    stderr = io.StringIO()
    with capture(stdout=stdout, stderr=stderr) as (_stdout, _stderr):
        printf(u"Hellø")
        printf_err(u"Hi, stdérr")
        assert _stdout is stdout
        assert _stderr is stderr
    
    assert stdout.getvalue() == u"Hellø\n"
    assert stderr.getvalue() == u"Hi, stdérr\n"

def test_capture_stderr():
    stdout = io.StringIO()
    with capture(stdout=stdout, stderr=STDOUT) as (_stdout, _stderr):
        printf(u"Hellø")
        libc.fflush(c_stdout_p)
        printf_err(u"Hi, stdérr")
        assert _stdout is stdout
        assert _stderr is None
    
    assert stdout.getvalue() == u"Hellø\nHi, stdérr\n"

def test_redirect_to_sys():
    stdout = io.StringIO()
    stderr = io.StringIO()
    with mock.patch('sys.stdout', stdout), mock.patch('sys.stderr', stderr), redirect_to_sys():
        printf(u"Hellø")
        printf_err(u"Hi, stdérr")
    
    assert stdout.getvalue() == u"Hellø\n"
    assert stderr.getvalue() == u"Hi, stdérr\n"

def test_redirect_everything():
    stdout = io.StringIO()
    stderr = io.StringIO()
    with mock.patch('sys.stdout', stdout), mock.patch('sys.stderr', stderr):
        redirect_everything_to_sys()
        printf(u"Hellø")
        printf_err(u"Hi, stdérr")
        stop_redirecting_everything()
    assert stdout.getvalue() == u"Hellø\n"
    assert stderr.getvalue() == u"Hi, stdérr\n"


