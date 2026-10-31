# Direct attention before increasing render quality

The previous draft reused a wide house/chamber composition and a small drift for most explanations. The models were readable, but the named parts stayed too small. The revised direction gives each mechanical noun a focal view and each camera change a reason: establish the system, inspect the cause, then reveal the result.

## Research and interpretation

- [Zack D Films' animator brief](https://zackdfilms.recruitee.com/o/3d-generalist) explicitly calls for craftsmanship in camera work, timing, look development and simulation. It links published Shorts as examples. This supports treating direction as authored production work rather than applying a generic zoom filter.
- [Animator Chris Reilly's production account](https://www.chrisreillyportfolio.com/zackdfilms.php) describes capturing attention in the first 1–2 seconds, followed by a substantive short explanation. He also describes reusable Blender templates and an automated render workflow. This supports an active opening and reusable scene rigs, rather than replacing consistent geometry with generated pictures.
- [How A Hydraulic Press Works](https://www.youtube.com/watch?v=CLDn6S0vkjU) is a relevant published example found during research. The execution environment could not play the YouTube video, so no claim of frame-by-frame viewing or measured cut statistics is made. The user's supplied storyboard remains the directly inspected visual reference.

The decisions below are our original interpretation, not a claim that Zack D Films uses this exact script, timing or camera formula. No narration or film footage is copied.

## Hidden-garage edit

The 12 narration sections still total 51 seconds. They now form a problem/solution chain: a disappearing car; unstable ground; reinforcement; the lifting problem; oil pressure; rain; drainage; the pinch point; beam interruption; concealment; a final return-and-hide demonstration.

| Beat | Directed visual |
| --- | --- |
| Arrival | Follow the moving car, finish parking, then move below grade as the lift descends. The car stays the subject. |
| Excavation / collapse | Push toward the empty chamber, cut to the crumbling soil, then show the resulting hole. |
| Reinforcement | Inspect the steel cage before pulling back to the concrete chamber. |
| Hydraulics | Hold on the pump; follow the oil line; inspect a telescopic cylinder through its blue shell; cut out to the car rising. |
| Drainage | Show the sump, then magnify the valve so its opening/closing action is visible. |
| Safety | Inspect the optical sensor; show the crate interrupting the beam; cut back to the stopped lift. |
| Concealment | Show descent, then the paving seam closing. |
| Payoff | Show the car return, reveal its descent, and finish on the ordinary-looking driveway. |

Close-up cutaways remove foreground car/deck geometry where it would conceal a component, while retaining the same world coordinates and modeled parts. Small-part shots use a broad diagnostic fill. Captions move to their declared safe zone at camera-beat boundaries. A quiet hold is intentional; constant motion is not required while a small mechanism acts.

## Reuse the direction file

Add `"direction": "direction.json"` to a story's `story.json`. It is optional; existing folders still work. The loader validates and hashes the file before rendering.

```json
{
  "schema_version": 1,
  "shots": {
    "S06": [
      {"at": 0, "view": "pump", "scale": 1.55, "end_scale": 1.5},
      {"at": 1.8, "view": "line", "move": 0.4},
      {"at": 2.7, "view": "cylinder", "move": 0.4},
      {"at": 4.7, "view": "lift", "scale": 7.8, "end_scale": 7.3}
    ]
  }
}
```

`at` is seconds from the beginning of that script section. The first beat starts at zero. `view` binds a camera rig to an actual modeled subject. `move` is arrival time in seconds: zero (the default) makes a cut; a positive value eases from the preceding rig, then holds the subject. `scale` is the vertical orthographic field in metres; smaller values magnify the subject. `end_scale` optionally adds a small push after arrival. A view tracks its moving subject automatically. Avoid overlapping travel or fractional-frame timing; both are rejected.

Garage views are `approach`, `driveway`, `chamber`, `excavation`, `soil`, `wall`, `load`, `pump`, `line`, `cylinder`, `lift`, `rim`, `flood`, `sump`, `valve`, `pinch`, `sensor`, `beam` and `seam`. The independent hydraulic lab supports `pump`, `line`, `cylinder` and `lift`. New asset adapters define their own anchors/rigs; narration alone does not invent a focal subject.

Use **mechanism** scope in **Render engineering story** for the short explanation review. It selects the garage's first `hydraulics` section, or the lab's first `extend` section, rebases it to zero and keeps its camera beats and narration. Uploaded full-story recordings and SRT files are cropped to the matching source interval. Automatic pull-request runs render this scope and the opening as separate review videos. Use **opening** to review the hook and **full** after reviewing the direction. Selecting a scope does not imply a render has completed; consult its actual workflow artifacts and reports.
