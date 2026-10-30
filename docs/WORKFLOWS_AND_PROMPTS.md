# API workflow guide and prompts

These JSON files are ComfyUI API-format graphs, not GUI workflow exports. Install compatible ComfyUI/custom nodes and obtain compatible third-party models under their own licenses. The names in the graphs are exact historical names, not bundled weights or guarantees that your installation supports them. Inspect every graph and configure locally before submission. No endpoint or credential is supplied.

## Supplied sources

- [Text-to-image](../workflows/supplied/image-t2i.json): byte-identical to supplied `image_flux3_klein_t2i_budnspud (1).json`. It retains its unrelated stock prompt and prompt-upsampling/layout branches: it is an archive, not a ready-to-run Bud n Spud prompt.
- [Image edit](../workflows/supplied/image-edit.json): byte-identical to `image_flux3_klein_image_edit_nextscene_budnspud.json`. Despite its filename, node 62 selects the chaos-scene adapter, and its stock dress/image/upsampler branches remain. This is not the executed next-scene adapter graph.
- [FastH3 OmniRef video](../workflows/supplied/video-h3.json): byte-identical to supplied `video_fasth3_ominiref_r2v_budnspud_FirstAndLast.json` (the `(1)` attachment is identical). Stock plane prompt and example image names remain. Although named FirstAndLast, its inputs are reference slots, not enforced first and last frames.
- [Fish voice API graph](../workflows/supplied/fish-voice.json): archived source graph used by the local project, not independently established as byte-identical to a current attachment; it retains its stock sample text.

## Real executed examples

The [start](../workflows/executed/start.json), [end](../workflows/executed/end.json), [background](../workflows/executed/background.json), [H3 video](../workflows/executed/video-h3.json), and [left](../workflows/executed/voice-left.json)/[right](../workflows/executed/voice-right.json) voice graphs are byte-identical copies of the local recorded submitted graphs. They contain exact generation prompts and seeds. Historical filenames refer to that server's input directory, so upload inputs and change LoadImage/LoadAudio names on your own server. The H3 graph used different voices from this kit; see [voice provenance](ASSETS_AND_PROVENANCE.md).

Start graph encodes a handmade-clay laundromat shot with both characters. Edit graph feeds actual input via node 54 to `ReferenceMultiLatent` node 17 and uses the next-scene adapter at node 62. The source project records the input hash and upload readback. For your own edits, set node 54 to your uploaded image and node 4 to your actual edit instruction; keep an independent record of what was submitted.

The recorded H3 graph uses `MiniMaxH3ReferenceToVideo` node 136, three image references (137/149/150), two audio references (151/152), prompt node 138 and seed 729037. It uses 8 sampling steps, Euler/simple, video/audio shift 12/3, and VSA; native frame quantization produced approximately 15.083 seconds, not exactly 15. References condition rather than constrain exact frames or speech. Hardware, custom nodes and third-party models must be compatible; no VRAM or runtime guarantee.

## Historical video prompt

The exact full prompt is in [node 138](../workflows/executed/video-h3.json). It maps picture 1 to the intended opening, picture 2 to the later state, picture 3 to the empty room; it maps audio 1 to the tall left character and audio 2 to the shorter right character, as voice references only. It requests a single funny stop-motion shot, no music or narrator, the following lines in sequence and an original mischievous laugh:

> Left: “This machine says I need boundaries.”  
> Right: “Mine says stop dating your laundry!”

The prompt is an instruction, not evidence of precise generated words or voice behavior. Check the generated media and license terms yourself; see [provenance](ASSETS_AND_PROVENANCE.md) and [rights](RIGHTS_AND_MODELS.md).
