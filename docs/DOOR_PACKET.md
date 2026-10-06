# External Door Packets

Revival can receive `static.door-packet/0.1` only as a **held external candidate**.

The adapter in `revival.door_packet` validates the exact v0 shape, refuses any packet that claims authority/requested effect or crosses private room material, and returns:

```text
external Scripture coordinate
        ↓
held candidate
        ↓
revivalAddress = null
authority = null
```

No source witness, lexeme, sense, referent, relation, projection, or interpretation is manufactured during import.

> **EXTERNAL DOOR != SOURCE WITNESS**

A later explicit Revival operation may attempt to resolve the coordinate against attributable Revival material. That is a separate act and is outside DOOR PACKET 001.
