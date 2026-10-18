from app.demo.replay import replay


async def test_the_replay_reports_the_demo_numbers():
    report = await replay("noise cancelling headphones")

    assert report.listings == 9
    assert (report.trusted, report.caution, report.danger) == (8, 0, 1)
    assert report.danger_ids == ["lst_vln_xm5"]
    assert report.picked_id == "lst_tgt_bsp"
    assert report.median_cents == 37449
    assert report.savings_cents == 19450


async def test_the_replay_is_deterministic():
    first = await replay("headphones")
    second = await replay("headphones")

    assert first.as_dict() == second.as_dict()


async def test_the_villain_is_never_the_pick():
    report = await replay("headphones")

    assert report.picked_id not in report.danger_ids


async def test_the_replay_supplies_its_own_settings(monkeypatch):
    """The replay must be offline even when the surrounding env is not."""

    def live_settings():
        raise AssertionError("the replay must not read the live settings")

    monkeypatch.setattr("app.sessions.orchestrator.get_settings", live_settings)

    report = await replay("headphones")

    assert report.listings == 9
