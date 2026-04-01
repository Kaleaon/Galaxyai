"""Tests for hyperlane/wormhole network and galaxy routing."""

from gma.galaxy import Galaxy


def test_hyperlane_path_uses_registered_domains():
    g = Galaxy()
    g.register_domain("a", position=(0.0, 0.0, 0.0))
    g.register_domain("b", position=(10.0, 0.0, 0.0))
    g.register_domain("c", position=(20.0, 0.0, 0.0))

    g.add_hyperlane("a", "b")
    g.add_hyperlane("b", "c")

    assert g.shortest_domain_path("a", "c") == ["a", "b", "c"]


def test_wormhole_can_be_selected_as_cheapest_path():
    g = Galaxy()
    g.register_domain("a", position=(0.0, 0.0, 0.0))
    g.register_domain("b", position=(10.0, 0.0, 0.0))
    g.register_domain("c", position=(20.0, 0.0, 0.0))

    g.add_hyperlane("a", "b", stability=0.9)
    g.add_hyperlane("b", "c", stability=0.9)
    g.add_wormhole("a", "c", stability=0.8, distance_multiplier=0.05)

    assert g.shortest_domain_path("a", "c") == ["a", "c"]


def test_galaxy_map_3d_contains_systems_and_lanes():
    g = Galaxy()
    g.register_domain("geography", position=(1.0, 2.0, 3.0))
    g.register_domain("astronomy", position=(5.0, 2.0, 1.0))
    g.add_hyperlane("geography", "astronomy")

    payload = g.galaxy_map_3d()
    assert "systems" in payload
    assert "lanes" in payload
    assert len(payload["systems"]) == 2
    assert len(payload["lanes"]) == 1
