import unittest

from revival.door_packet import hold_door_packet


PACKET = {
    "schema": "static.door-packet/0.1",
    "packetRef": "door:upper-room:001",
    "source": {
        "system": "upper-room",
        "sourceRef": "selection:gen-1-1",
        "doorKind": "selection",
    },
    "anchor": {
        "translationId": "webp",
        "book": "GEN",
        "chapter": 1,
        "startVerse": 1,
        "endVerse": 1,
    },
    "disclosure": {
        "includesPrivateText": False,
        "includesHumanNote": False,
        "includesParticipantIdentity": False,
    },
    "authority": None,
    "requestedEffect": None,
}


class DoorPacketTests(unittest.TestCase):
    def test_holds_external_door_without_promoting_it_to_source_or_interpretation(self):
        candidate = hold_door_packet(PACKET)
        self.assertEqual(candidate["schema"], "revival.external-door-candidate/0.1")
        self.assertEqual(candidate["packetRef"], PACKET["packetRef"])
        self.assertEqual(candidate["anchor"], PACKET["anchor"])
        self.assertEqual(candidate["status"], "held")
        self.assertIsNone(candidate["revivalAddress"])
        self.assertIsNone(candidate["authority"])
        self.assertEqual(candidate["claimBoundary"], "external door != source witness")

    def test_refuses_packets_that_smuggle_private_or_authoritative_payload(self):
        bad = {**PACKET, "authority": "upper-room"}
        with self.assertRaisesRegex(ValueError, "authority"):
            hold_door_packet(bad)

        bad = {**PACKET, "disclosure": {**PACKET["disclosure"], "includesHumanNote": True}}
        with self.assertRaisesRegex(ValueError, "private"):
            hold_door_packet(bad)


if __name__ == "__main__":
    unittest.main()
