from app.ai.prefilter import should_process


def test_skip_outbound():
    ok, reason = should_process("Can we meet?", "outbound", "text", False)
    assert not ok
    assert reason == "outbound"


def test_skip_short_social():
    ok, reason = should_process("ok", "inbound", "text", False)
    assert not ok


def test_process_meeting_keyword():
    ok, reason = should_process("Can we meet tomorrow?", "inbound", "text", False)
    assert ok
    assert reason == "action_keyword"


def test_process_voice_note():
    ok, reason = should_process("", "inbound", "voice", False)
    assert ok
    assert reason == "voice_note"


def test_skip_media_no_caption():
    ok, reason = should_process("", "inbound", "image", False)
    assert not ok


def test_process_deadline_keyword():
    ok, reason = should_process("The report is due tomorrow EOD", "inbound", "text", False)
    assert ok


def test_skip_too_short():
    ok, reason = should_process("Hi!", "inbound", "text", False)
    assert not ok
