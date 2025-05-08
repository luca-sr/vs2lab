import zmq
import time
import random
import constPipe

context = zmq.Context()
socket = context.socket(zmq.PUSH)
socket.bind(f"tcp://*:{constPipe.SPLITTER_OUT_PORT}")

word_list = [
    "abandon", "ability", "absorb", "accommodate", "accomplish", "accuracy", "adventure", "airplane", "allegiance", "anxiety", 
    "appeal", "applause", "arena", "arrange", "astound", "balloon", "banish", "barrier", "beacon", "beauty", 
    "bliss", "brilliant", "breathe", "brilliant", "calm", "celebrate", "clarity", "climb", "comfort", "commit", 
    "compete", "courage", "creative", "dance", "deepen", "defend", "dream", "duty", "echo", "elegant", 
    "enlighten", "envision", "equality", "evolve", "fascinate", "feather", "flight", "forest", "frost", "freedom", 
    "glorious", "grace", "grip", "guide", "harmony", "honor", "inspire", "jazz", "journey", "kindness", 
    "legend", "lemon", "lightning", "limit", "mansion", "marvel", "moment", "nature", "ocean", "optimistic", 
    "peace", "piano", "quest", "quiet", "respect", "reverence", "reward", "strength", "talent", "tender", 
    "trust", "unity", "vision", "whisper", "wisdom", "yarn", "zeal", "zenith", "anchor", "angel", 
    "apple", "art", "balance", "benefit", "bless", "brave", "brilliance", "breathe", "bright", "calm", 
    "capable", "celestial", "celebrate", "compassion", "confident", "content", "courage", "creativity", 
    "dare", "defend", "delight", "eager", "embrace", "endless", "empower", "enrich", "flame", 
    "flare", "flourish", "force", "fortune", "freedom", "glory", "gratitude", "grit", "hope", 
    "inspire", "invention", "joy", "legacy", "leap", "love", "loyalty", "marvel", "moment", 
    "mystery", "navigate", "nurture", "optimism", "paradise", "peace", "purpose", "radiate", 
    "rejuvenate", "reverence", "romance", "strength", "surprise", "together", "visionary", "warmth", 
    "whimsy", "wise", "wonder", "worthy", "yearn", "zephyr", "zone", "zealot", "affection", 
    "alter", "ambition", "awaken", "bloom", "blissful", "breathe", "conquer", "connect", 
    "defiant", "delightful", "dreamer", "dreams", "endure", "explore", "embrace", "flourish", 
    "focus", "guide", "growth", "hopeful", "imagine", "inspire", "joyful", "kindness", 
    "laugh", "leap", "light", "love", "magnificent", "meaning", "momentum", "mystical", 
    "outreach", "peaceful", "rejuvenate", "refresh", "renew", "resilient", "serenity", 
    "strengthen", "support", "thrive", "unfold", "uplift", "vision", "vital", "vibrant", 
    "wholesome", "zeal", "zone", "adore", "aim", "assure", "brilliance", "celebrate", 
    "dedicate", "evolve", "focus", "flourish", "friend", "gather", "grace", "grow", 
    "ignite", "love", "peaceful", "radiate", "renew", "spark", "strength", "unite", 
    "whole", "wise", "zeal", "whimsy", "glisten", "glow", "sparkle", "whisper", 
    "inspire", "harmony", "dream", "empower", "breathe", "vision", "bloom", "ambition"
]

def generate_random_sentence(word_count=10):
    sentence = ' '.join(random.choice(word_list) for _ in range(word_count))
    return sentence.capitalize() + '.'

print("Splitter started...")
time.sleep(1)

for i in range(20):
    msg = generate_random_sentence()
    print(f"Splitter sent: {msg}")
    socket.send_string(msg)
    time.sleep(0.2)
