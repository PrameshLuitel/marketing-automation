import os
import json
import subprocess
import asyncio
from loguru import logger
from dotenv import load_dotenv
import edge_tts

load_dotenv()

# Global progress tracker for video generation
VIDEO_PROGRESS = {}

class VideoGenerator:
    """Generates a 9:16 viral motion graphics video using Remotion and edge-tts."""
    
    def __init__(self, profile_data: dict, run_id: str = "default"):
        self.profile = profile_data.get("company", {})
        self.run_id = run_id
        self.backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.project_root = os.path.dirname(self.backend_dir)
        self.renderer_dir = os.path.join(self.project_root, "video-renderer")
        self.public_dir = os.path.join(self.renderer_dir, "public", "assets")
        os.makedirs(self.public_dir, exist_ok=True)

    def _update_progress(self, step: int, total: int, message: str, detail: str = ""):
        """Update the global progress tracker."""
        VIDEO_PROGRESS[self.run_id] = {
            "step": step,
            "total_steps": total,
            "message": message,
            "detail": detail,
            "percent": int((step / total) * 100),
        }
        logger.info(f"[Video:{self.run_id}] Step {step}/{total}: {message}")

    async def generate_async(self, brief: dict):
        video_scenes = brief.get("video_scenes", [])
        brand_config = brief.get("brand_config", {})
        requested_duration = brief.get("video_duration_seconds", 15)
        
        if not video_scenes:
            return {"error": "No video scenes dict provided"}

        total_steps = len(video_scenes) + 3  # prep + N TTS + render + finalize
        self._update_progress(1, total_steps, "Preparing Remotion props...", "Setting up dynamic brand colors and typography")

        logo_url = self.profile.get("logo_url", "")
        if logo_url and ("/outputs/assets/" in logo_url):
            filename = logo_url.split("/")[-1].split("?")[0]
            local_path = os.path.abspath(os.path.join(self.backend_dir, "data", "outputs", "assets", filename))
            if os.path.exists(local_path):
                import shutil
                dest_path = os.path.join(self.public_dir, filename)
                shutil.copy2(local_path, dest_path)
                logo_url = f"/assets/{filename}"


        # 1. Prepare Remotion props (prioritize brand_config from LLM)
        remotion_props = {
            "template_id": brief.get("template_id") or "dynamic_agency",
            "brand_primary": brand_config.get("primary_color") or self.profile.get("brand_primary_color", "#FF6B6B"),
            "brand_secondary": brand_config.get("secondary_color") or self.profile.get("brand_secondary_color", "#4285F4"),
            "brand_font": brand_config.get("font_family") or self.profile.get("brand_font_family", "Inter"),
            "logo_url": logo_url,
            "bgm_track": brief.get("video_brand_config", {}).get("bgm_track", "electronic.mp3"),
            "bg_effect": brief.get("video_brand_config", {}).get("bg_effect", "mesh"),
            "text_anim": brief.get("video_brand_config", {}).get("text_anim", "fade"),
            "scenes": []
        }
        
        target_fps = 30
        target_total_frames = requested_duration * target_fps
        base_frames_per_scene = target_total_frames // len(video_scenes) if video_scenes else 90

        product_image_urls = self.profile.get("product_image_urls", [])

        for i, scene in enumerate(video_scenes):
            step = i + 2
            raw_voice_txt = scene.get("voiceover_prompt", "").strip()
            import re
            voice_txt = re.sub(r'\[.*?\]|\(.*?\)', '', raw_voice_txt).strip()
            audio_url = ""
            audio_frames = 0
            
            if voice_txt:
                audio_filename = f"audio_{self.run_id}_{i}.mp3"
                audio_path = os.path.join(self.public_dir, audio_filename)
                try:
                    self._update_progress(step, total_steps, f"Generating voiceover {i+1}/{len(video_scenes)}...", f'"{voice_txt[:60]}..."')
                    communicate = edge_tts.Communicate(voice_txt, "en-US-ChristopherNeural")
                    await communicate.save(audio_path)
                    audio_url = f"/assets/{audio_filename}"
                    
                    # Estimate audio length roughly (130 words per min = ~2.1 words per sec)
                    word_count = len(voice_txt.split())
                    estimated_seconds = max(2.0, word_count / 2.1)
                    audio_frames = int(estimated_seconds * target_fps)
                except Exception as e:
                    logger.error(f"TTS generation failed: {e}")
                    self._update_progress(step, total_steps, f"Voiceover {i+1} failed, continuing...", str(e))
            
            # Scene duration is the LONGER of the requested slice or the voiceover duration
            # (but clamp to a reasonable max to avoid infinitely long output if LLM is verbose)
            final_duration = max(base_frames_per_scene, audio_frames)
            final_duration = min(final_duration, target_total_frames) # never let 1 scene exceed max video length

            # Attach an image sequentially if available
            scene_image_url = ""
            if product_image_urls:
                raw_img_url = product_image_urls[i % len(product_image_urls)]
                if raw_img_url and ("/outputs/assets/" in raw_img_url):
                    img_filename = raw_img_url.split("/")[-1].split("?")[0]
                    img_local_path = os.path.abspath(os.path.join(self.backend_dir, "data", "outputs", "assets", img_filename))
                    if os.path.exists(img_local_path):
                        import shutil
                        dest_img_path = os.path.join(self.public_dir, img_filename)
                        shutil.copy2(img_local_path, dest_img_path)
                        scene_image_url = f"/assets/{img_filename}"
                else:
                    scene_image_url = raw_img_url

            remotion_props["scenes"].append({
                "text": scene.get("text", ""),
                "durationInFrames": final_duration,
                "imageUrl": scene_image_url,
                "audioUrl": audio_url,
                "sfx": scene.get("sfx", "")
            })

        # --- RIGOROUS ASSET VALIDATION ---
        # Prevent Remotion from fatally crashing if AI requests a non-existent audio track
        bgm = remotion_props.get("bgm_track")
        if bgm and bgm != "none":
            if not os.path.exists(os.path.join(self.public_dir, bgm)):
                logger.warning(f"Missing BGM track '{bgm}', omitting to prevent render crash.")
                remotion_props["bgm_track"] = ""
                
        for sc in remotion_props.get("scenes", []):
            sfx = sc.get("sfx")
            if sfx and sfx != "none":
                if not os.path.exists(os.path.join(self.public_dir, sfx)):
                    logger.warning(f"Missing SFX '{sfx}', omitting to prevent render crash.")
                    sc["sfx"] = ""
        # ---------------------------------

        # Save props file
        props_path = os.path.join(self.renderer_dir, f"input-props_{self.run_id}.json")
        with open(props_path, "w") as f:
            json.dump(remotion_props, f)

        # 2. Render Remotion Video
        render_step = len(video_scenes) + 2
        self._update_progress(render_step, total_steps, "Rendering video with Remotion...", "This may take 30-60 seconds")

        output_filename = f"video_{self.run_id}.mp4"
        outputs_dir = os.path.join(self.backend_dir, "data", "outputs")
        os.makedirs(outputs_dir, exist_ok=True)
        output_mp4 = os.path.join(outputs_dir, output_filename)
        
        try:
            # Build the env with /usr/local/bin in PATH so node/npx are found
            env = os.environ.copy()
            env["PATH"] = f"/usr/local/bin:/opt/homebrew/bin:{env.get('PATH', '')}"
            
            process = await asyncio.create_subprocess_exec(
                "npx", "remotion", "render", "src/index.ts", "Main", output_mp4, f"--props=./input-props_{self.run_id}.json",
                cwd=self.renderer_dir,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=300)
            
            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown error"
                logger.error(f"Remotion render failed: {error_msg}")
                self._update_progress(render_step, total_steps, "Render failed!", error_msg[:200])
                return {"error": "Remotion render failed."}
                
            logger.info(f"Remotion stdout: {stdout.decode()[-200:]}")
        except asyncio.TimeoutError:
            logger.error("Remotion render timed out.")
            self._update_progress(render_step, total_steps, "Render timed out!", "Render took more than 300s.")
            return {"error": "Remotion render timed out."}
        except FileNotFoundError:
            logger.error("npx not found. Ensure Node.js is installed and in PATH.")
            self._update_progress(render_step, total_steps, "npx not found!", "Ensure Node.js is installed.")
            return {"error": "npx not found."}

        # 3. Finalize
        self._update_progress(total_steps, total_steps, "Video ready!", f"Output: {output_filename}")

        return {
            "type": "video",
            "stream_url": f"/outputs/{output_filename}",
            "description": "A high-impact 9:16 viral motion graphics video with synchronized AI voiceover."
        }
