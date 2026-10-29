# Full-episode story contract

The viewer should understand what each addition fixes, see the result on the
inventor, then encounter the next problem. All features are cumulative; changing
a shot never replaces an earlier capability or swaps the inventor/backyard.

| Time | Addition | Visible result | Next problem |
| --- | --- | --- | --- |
| 0–6 s | Cardboard foundation and drawing | A simple suit; a loose flap folds | Not sturdy enough |
| 6–12 s | Metal over the cardboard | Plates reinforce the same suit; effortful step | Excess weight |
| 12–18 s | Assisted joints | Hinges/pistons appear; movement improves | Sustaining movement |
| 18–24 s | Fictional power cell | Powered indicators; suit gets hot, hand rises to forehead, sweat | Heat |
| 24–30 s | Cooling pack | Fan and fins added; sweat/heat settle; hand lowers | Still grounded |
| 30–36 s | Fictional hover modules | New boot modules lift him; pronounced balance wobble | No stable control |
| 36–42 s | Stabilization/control pods | Pods added; wobble settles into a steady hover | Ready for flight |
| 42–48 s | All upgrades retained | Titanium-gray/turquoise suit rises above the same yard | Closing warranty joke |

Each six-second beat has complete story text in `src/story.ts`. The renderer
burns in timed word captions and short addition/result annotations; the planner
exports the complete text as SRT. The current episode is silent: the text called
`narration` is the story transcript, not a generated voice track.

The cardboard stays under the metal, including visible edge/backing pieces.
Metal remains when joints are added; joints remain under power/cooling; powered
boots acquire hover modules only at the hover beat. Stabilizers appear only
after the failed hover test. Controlled flight requires stabilization.

Heat is a separate interval from its cooling solution. The rig reaches toward
the forehead, sweat appears, and the power indicator turns warm. The following
cooling beat adds a spinning fan/fins while heat and the hand-to-forehead reaction
subside. It is not a list of unrelated armor skins.

All technologies involved in flight are imaginary. There are no real materials
specifications, thrust calculations, wiring instructions or human-flight recipes.
