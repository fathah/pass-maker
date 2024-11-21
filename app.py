from flask import Flask, request, send_file
from PIL import Image, ImageDraw, ImageFont
import qrcode
import os

app = Flask(__name__)

# Ensure the font file is available in the same folder
FONT_PATH = "font.ttf"  # Replace with a suitable font path if not present
PASS_IMAGE_PATH = "pass.png"

@app.route('/generate-pass', methods=['GET'])
def generate_pass():
    # Get the parameters
    user_id = request.args.get('id')
    name = request.args.get('name')
    emirate = request.args.get('emirate')

    if not user_id or not name or not emirate:
        return "Missing parameters: id, name, and emirate are required.", 400

    try:
        # Load the base image
        base_image = Image.open(PASS_IMAGE_PATH)
        draw = ImageDraw.Draw(base_image)
        width, height = base_image.size

        # Generate QR Code
        qr = qrcode.QRCode(box_size=10, border=0)
        qr.add_data(user_id)
        qr.make(fit=True)
        qr_image = qr.make_image(fill="black", back_color="white").convert("RGB")
        qr_size = 280
        qr_image = qr_image.resize((qr_size, qr_size))

        # Position QR Code at bottom center
        qr_x = 220
        qr_y = 780
        base_image.paste(qr_image, (qr_x, qr_y))

        # Load font
        try:
            font_large = ImageFont.truetype(FONT_PATH, 40)
            font_small = ImageFont.truetype(FONT_PATH, 30)
        except IOError:
            return "Font file not found. Please add a font file to the folder.", 500

        # Add name (centered, wrap text if too long)
        name = name.upper()
        name_lines = wrap_text(draw, name, font_large, width - 40)
        name_height = 0
        for i, line in enumerate(name_lines):
            text_width, text_height = draw.textsize(line, font=font_large)
            draw.text(((width - text_width) / 2, qr_y - 150 + (i * text_height)),
                      line, font=font_large, fill="white")
            name_height += text_height

        # Add emirate below name
        emirate = emirate.upper()
        text_width, text_height = draw.textsize(emirate, font=font_small)
        draw.text(((width - text_width) / 2, qr_y - 150 + name_height),
                  emirate, font=font_small, fill="#FCFF62")

        # Save the updated image temporarily
        output_path = "output.png"
        base_image.save(output_path)

        # Return the image
        return send_file(output_path, mimetype='image/jpeg')

    except Exception as e:
        return f"Error generating pass: {str(e)}", 500

def wrap_text(draw, text, font, max_width):
    """
    Wrap text to fit within a maximum width.
    """
    words = text.split()
    lines = []
    current_line = words[0]

    for word in words[1:]:
        if draw.textsize(f"{current_line} {word}", font=font)[0] <= max_width:
            current_line += f" {word}"
        else:
            lines.append(current_line)
            current_line = word

    lines.append(current_line)
    return lines

if __name__ == '__main__':
    app.run(debug=True)
