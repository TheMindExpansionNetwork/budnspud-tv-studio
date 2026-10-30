# Starter references and provenance

The images and audition voices are creator-supplied project outputs, not model weights. See [reference sheet](../assets/images/reference-sheet.jpg). The sheet is ordered background, start, end. The individual PNGs retain their original ComfyUI prompt metadata.

| File | Role | Source and actual observation |
|---|---|---|
| [start.png](../assets/images/start.png) | Picture 1 / intended opening | `budnspud-life-advice-blooper/assets/start.png`; two adult clay characters, tall left in blue and red, shorter right in a beanie and rainbow hoodie. Generated with [executed start graph](../workflows/executed/start.json), seed 729032. |
| [end.png](../assets/images/end.png) | Picture 2 / later state | `assets/end.png` in the same source project, image-conditioned edit of start, [executed edit](../workflows/executed/end.json), seed 729036. Tall figure has both hands on/beside head, not the requested one hand. |
| [background.png](../assets/images/background.png) | Picture 3 / empty environment | `assets/environment_retry.png` from that project, [executed graph](../workflows/executed/background.json), seed 729035. Independent render, not guaranteed identical geometry to the actor set. |
| [left.wav](../assets/voices/left.wav) | Synthetic voice anchor for tall/left character | `ref-voice-v2/left.wav`, PCM conversion of an independently generated Fish Drama 3 output. Intended words: “I checked the numbers twice, and honestly, this plan is only slightly ridiculous.” [Executed voice graph](../workflows/executed/voice-left.json), seed 9321061. |
| [right.wav](../assets/voices/right.wav) | Synthetic voice anchor for shorter/right character | `ref-voice-v2/right.wav`, PCM conversion of an independently generated Fish Drama 3 output. Intended words: “Well, the robot has a point. Maybe we should ask the toaster for a second opinion.” [Executed voice graph](../workflows/executed/voice-right.json), seed 9321062. |

The voice clips are approximately 4.458 and 4.226 seconds, respectively; they were not padded. Source project reports offline ASR recovered the intended words, not human verification. They are independent synthetic auditions, not recordings of or prompted to imitate real people; audible distinctness, accent and acting remain unverified. Subject labels are positional, not a claim about which named character is Bud or Spud.

**Important voice provenance:** the [historical executed H3 graph](../workflows/executed/video-h3.json) used a different, earlier pair of synthetic WAVs named `life-advice-voice_left.wav` and `life-advice-voice_right.wav`, not the v2 auditions included here. The H3 graph has not been executed with these v2 anchors. To try these anchors, upload the two included WAVs and update nodes 151/152; this is a new, unverified run, not a reproduction of the historical output.

The original local project records successful source-to-end conditioning and input upload/readback; its retained H3 history reports a completed native 15.083-second clip and its later exact-15-second derivative. Automated transcription recovered both intended dialogue lines but also possible additional utterances. Human listening, speaker attribution, laughter, lip sync and exact endpoint matching remain unverified; sampled frames alone cannot establish these. The video itself is not included in this kit. No claim is made that an H3 job was run during packaging.

[SHA-256 manifest](SHA256SUMS) records the shipped bytes. Source images and audio were copied byte-for-byte; the output's generation prompts are in the executed graphs rather than reconstructed captions. The source project and its full receipts remain local and are not part of this public starter kit.
