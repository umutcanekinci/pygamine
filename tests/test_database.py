"""Unit tests for Database: a thin sqlite3 wrapper that connects to
databases/<name>.db (relative to cwd, auto-creating the folder).
"""
from __future__ import annotations

import sqlite3

import pytest

from pygame_core.database import Database


@pytest.fixture(autouse=True)
def _isolate_cwd(tmp_path, monkeypatch):
    """connect() hardcodes a cwd-relative 'databases/' folder -- isolate
    every test in its own tmp_path so nothing touches the real repo."""
    monkeypatch.chdir(tmp_path)


# ── connect ──────────────────────────────────────────────────────────


def test_connect_creates_the_databases_folder(tmp_path):
    db = Database("test")
    assert db.connect() is True
    assert (tmp_path / "databases").is_dir()
    assert (tmp_path / "databases" / "test.db").exists()


def test_connect_reuses_an_existing_databases_folder(tmp_path):
    (tmp_path / "databases").mkdir()
    db = Database("test")
    assert db.connect() is True  # must not raise just because the dir already exists


def test_connect_sets_a_real_sqlite_connection():
    db = Database("test")
    db.connect()
    assert isinstance(db.connection, sqlite3.Connection)


def test_connect_returns_false_on_failure(monkeypatch):
    def _raise(*args, **kwargs):
        raise sqlite3.OperationalError("simulated failure")

    monkeypatch.setattr(sqlite3, "connect", _raise)
    db = Database("test")
    assert db.connect() is False


# ── get_cursor ──────────────────────────────────────────────────────────


def test_get_cursor_before_connect_raises_assertion_error():
    db = Database("test")
    with pytest.raises(AssertionError):
        db.get_cursor()


def test_get_cursor_after_connect_returns_a_real_cursor():
    db = Database("test")
    db.connect()
    assert isinstance(db.get_cursor(), sqlite3.Cursor)


# ── execute ──────────────────────────────────────────────────────────


def test_execute_runs_real_sql():
    db = Database("test")
    db.connect()
    db.execute("CREATE TABLE t (id INTEGER)")
    db.execute("INSERT INTO t VALUES (?)", (42,))
    db.commit()

    rows = db.get_cursor().execute("SELECT * FROM t").fetchall()
    assert rows == [(42,)]


def test_execute_invalid_sql_raises_systemexit():
    db = Database("test")
    db.connect()
    with pytest.raises(SystemExit):
        db.execute("THIS IS NOT VALID SQL")


def test_execute_before_connect_raises_systemexit_not_assertion_error():
    """get_cursor() raises AssertionError when unconnected, but execute()'s
    own broad `except Exception` catches it (AssertionError is an Exception
    subclass) and converts it into sys.exit() -- so this surfaces as
    SystemExit, not AssertionError, which is easy to miss if you only read
    get_cursor() in isolation."""
    db = Database("test")
    with pytest.raises(SystemExit):
        db.execute("SELECT 1")


# ── execute_safely ──────────────────────────────────────────────────────


def test_execute_safely_without_fetch_returns_none():
    db = Database("test")
    result = db.execute_safely("CREATE TABLE t (id INTEGER)")
    assert result is None


def test_execute_safely_with_fetch_returns_rows():
    db = Database("test")
    db.execute_safely("CREATE TABLE t (id INTEGER)")
    db.execute_safely("INSERT INTO t VALUES (?)", params=(7,))

    rows = db.execute_safely("SELECT * FROM t", fetch=True)

    assert rows == [(7,)]


def test_execute_safely_disconnects_after_each_call():
    """execute_safely connects, runs the query, then disconnects -- but
    disconnect() only closes the underlying sqlite3 connection, it doesn't
    reset self.connection back to None. So get_cursor() afterward doesn't
    fail with "Database not connected" (that assertion checks for None) --
    it gets past the assertion and fails on the closed connection itself
    with sqlite3.ProgrammingError instead."""
    db = Database("test")
    db.execute_safely("CREATE TABLE t (id INTEGER)")

    with pytest.raises(sqlite3.ProgrammingError):
        db.get_cursor()


def test_execute_safely_exits_when_connect_fails(monkeypatch):
    def _raise(*args, **kwargs):
        raise sqlite3.OperationalError("simulated failure")

    monkeypatch.setattr(sqlite3, "connect", _raise)
    db = Database("test")
    with pytest.raises(SystemExit):
        db.execute_safely("SELECT 1")


# ── commit / disconnect ─────────────────────────────────────────────


def test_commit_before_connect_raises_assertion_error():
    db = Database("test")
    with pytest.raises(AssertionError):
        db.commit()


def test_disconnect_before_connect_raises_assertion_error():
    db = Database("test")
    with pytest.raises(AssertionError):
        db.disconnect()


def test_disconnect_actually_closes_the_connection():
    db = Database("test")
    db.connect()
    db.disconnect()
    with pytest.raises(sqlite3.ProgrammingError):
        db.connection.execute("SELECT 1")  # closed connections reject new queries
