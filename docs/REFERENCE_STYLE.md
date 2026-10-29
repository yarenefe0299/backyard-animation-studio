# Visual direction from the supplied screenshots

The user's three screenshots are the visual target for the existing original
backyard episode. They show human proportions, a subdued material palette,
textured earth sections, clear directional shadows, moving scene cameras and
bold white, black-outlined word captions. The earlier giant-headed toy figure,
smooth display platform and persistent title layout were rejected.

This revision changes the actual scene and mesh pipeline:

- Detailed CC0 human topology with continuous skinned shoulders, elbows, wrists,
  fingers, knees, neck and facial bones; original workwear and armor.
- Grounding from deformed sole vertices; armor attached to the same bone hierarchy.
- Unit-space beveled panels with outward normals, matte titanium-gray materials,
  turquoise accents and procedural studio reflections.
- Original noise-based soil and grass maps, a vertical earth cutaway, sky haze,
  quieter fence/shed colors and instanced individual leaves.
- Wide establishing move, closer action shots and a low hover shot. Short white
  outlined word captions replace the large title card and caption boxes.
- A continuous cardboard fall and a paper release calculated from the actual
  wrist transform, independent of frame render order.

The screenshots establish appearance, not motion data. This is an original
implementation targeting that treatment; it is not a verified frame-for-frame
match. No visual-quality acceptance is claimed from software tests alone.

## Review gate

Render only the ten-second preview on GitHub Actions. Review all seven extracted
frames plus the complete motion before extending the episode. Check head and hand
anatomy, eye placement, workwear boundaries, panel contact, falling prop continuity,
foot contact/landing, caption placement, soil texture scale and runner duration.
If the original human's vertex-colored workwear is too close-fitting, create a
proper garment shell before accepting the character. Facial deformation and hand
contact need visual review; numeric rig tests cannot establish their naturalness.
The preview still has no voice or sound track.
