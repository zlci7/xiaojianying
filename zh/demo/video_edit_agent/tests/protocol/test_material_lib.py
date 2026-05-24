from src.protocol.material_lib import MaterialClip, MaterialLib


class TestMaterialClip:
    def test_from_dict(self):
        data = {
            "clip_id": "mat_0042",
            "source": "DSC_0021.mp4",
            "in": "00:05.2",
            "out": "00:08.5",
            "duration": 3.3,
            "quality_score": 6,
            "shot_type": "drone_wide",
            "content_tags": ["scenery", "sunset"],
            "motion": {"direction": "push_forward", "speed": "medium"},
            "aesthetic_score": 7,
            "usable": True,
            "issues": [
                {"stability": {"level": "medium", "suggested_fix": "stabilize"}},
            ],
            "notes": "good clip",
        }
        clip = MaterialClip.from_dict(data)
        assert clip.clip_id == "mat_0042"
        assert clip.shot_type == "drone_wide"
        assert clip.usable is True
        assert len(clip.issues) == 1

    def test_material_lib_filter_usable(self):
        clip1 = MaterialClip(clip_id="m1", source="a.mp4", usable=True)
        clip2 = MaterialClip(clip_id="m2", source="b.mp4", usable=False)
        clip3 = MaterialClip(clip_id="m3", source="c.mp4", usable=True)
        lib = MaterialLib(clips=[clip1, clip2, clip3])
        usable = lib.usable_clips()
        assert len(usable) == 2

    def test_material_lib_filter_by_tags(self):
        clip1 = MaterialClip(clip_id="m1", source="a.mp4", content_tags=["scenery", "sunset"])
        clip2 = MaterialClip(clip_id="m2", source="b.mp4", content_tags=["food"])
        lib = MaterialLib(clips=[clip1, clip2])
        result = lib.filter_by_tags(["scenery"])
        assert len(result) == 1
        assert result[0].clip_id == "m1"
