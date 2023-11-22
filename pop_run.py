#!/usr/bin/env python3
#Author: Rafat A. Eissa

'''
	This package 
'''

import qrcode
from PIL import Image, ImageColor
from io import BytesIO
import pandas as pd
import zlib
import base64
import numpy as np
import argparse

# loading input file
def genotyping_data(filename):
    genotypes = pd.read_csv(filename, index_col=1)
    genotypes.index.name='MarkerName'
    # Replacing every missing allele with "3"
    genotypes = genotypes.replace("-", 3)

    # Remove each row that has the same value
    genotypes = genotypes[~genotypes.apply(lambda row: len(set(row)) == 1, axis=1)]
    # Your DataFrame (assuming it's named df)
    # Convert the DataFrame to a string
    def compress(data):
      data_string = data.to_csv(index=True)
      data_string = zlib.compress(data_string.encode())
      encoded_data = base64.b64encode(data_string).decode()
      compressed_df = pd.DataFrame(data={'CompressedData': [encoded_data]})
      return compressed_df
    return compress(genotypes), compress(genotypes.transpose())

def qrdecoding(markers, lines):

    def generate_colored_qr_code(data, color):
      qr = qrcode.QRCode(
          version=1,
          error_correction=qrcode.constants.ERROR_CORRECT_L,
          box_size=10,
          border=4,
      )
      qr.add_data(data)
      qr.make(fit=True)
      img = qr.make_image(fill_color=color, back_color="white")
      return img

    def combine_qr_codes(qr1,qr2):
      qr_code1 = Image.open(qr1)
      # qr_code1.save(output, format='PNG')

      qr_code2 = Image.open(qr2)
      # qr_code2.save(output, format='PNG')

      # Resize the images to the same dimensions
      width, height = max(qr_code1.size, qr_code2.size)
      qr_code1 = qr_code1.resize((width, height))
      qr_code2 = qr_code2.resize((width, height))

      # Convert the images to RGB format to ensure they have the same color channels
      qr_code1 = qr_code1.convert("RGB")
      qr_code2 = qr_code2.convert("RGB")
      qr_array1 = np.array(qr_code1)
      qr_array2 = np.array(qr_code2)
      combined_array = np.zeros_like(qr_array1)
      for i in range(width):
          for j in range(height):
              # Get the RGB values of each pixel in both arrays
              rgb1 = qr_array1[j, i]
              rgb2 = qr_array2[j, i]

              # If a pixel is black, leave it as it is
              if np.array_equal(rgb1, [0, 0, 0]) and np.array_equal(rgb2, [0, 128, 0]) :
                  combined_array[j, i] = [0, 0, 0]
              # If the pixel found in the black only make it orange
              elif np.array_equal(rgb1, [0, 0, 0]) : combined_array[j,i] = (255, 165, 0)

              else:
                  # Calculate the average of the RGB values to blend the colors
                  combined_array[j, i] = (np.array(rgb1) + np.array(rgb2))


      return combined_array

    # Convert the images to numpy arrays for manipulation
    markers_qr = generate_colored_qr_code(markers, "black")
    markers_qr.save("markers_qr.png")
    lines_qr = generate_colored_qr_code(lines, "green")
    lines_qr.save("lines.png")
    combined_qr_array = combine_qr_codes("markers_qr.png", "lines.png")
    combined_qr_code = Image.fromarray(combined_qr_array.astype('uint8'))
    combined_qr_code.save("combined_qr_code.png")
def encode_qr(combined_qr):
  combined_qr_code = Image.open(combined_qr)

  # Convert the image to RGB format
  combined_qr_code = combined_qr_code.convert("RGB")

  # Convert the image to a numpy array for manipulation
  combined_qr_array = np.array(combined_qr_code)
# Create arrays for the two original QR codes
  qr_array1 = np.zeros_like(combined_qr_array)
  qr_array2 = np.zeros_like(combined_qr_array)
  width = combined_qr_array.shape[0]
  height = combined_qr_array.shape[1]
  for i in range(width):
      for j in range(height):
          # Get the RGB value of the combined QR code pixel
          combined_rgb = combined_qr_array[j, i]

          # If the pixel is black in the combined QR code, set the corresponding pixel in both arrays to black
          if np.array_equal(combined_rgb, [254,254,254]):
              qr_array1[j, i] = [255,255,255]
              qr_array2[j, i] = [255,255,255]
          elif np.array_equal(combined_rgb, [0, 0, 0]):
              qr_array1[j, i] = [0, 0, 0]
              qr_array2[j, i] = [0, 128, 0]
          elif np.array_equal(combined_rgb, [255, 165, 0]):
              qr_array1[j, i] = [0, 0, 0]
              qr_array2[j, i] = [255,255,255]
          elif np.array_equal(combined_rgb, [255, 127, 255]):
              qr_array1[j, i] = [255,255,255]
              qr_array2[j, i] = [0,128,0]
  encoded_qr1_image = Image.fromarray(qr_array1)
  encoded_qr2_image = Image.fromarray(qr_array2)
  encoded_qr1_image.save("encoded_qr1.png")
  encoded_qr2_image.save("encoded_qr2.png")
  
  
def main():
  # Print popAllele Version
  print("""
  _______                       _       __   __         __         
  |_   __ \                     / \     [  | [  |       [  |        
    | |__) | .--.   _ .--.     / _ \     | |  | | .---.  | | .---.  
    |  ___// .'`\ \[ '/'`\ \  / ___ \    | |  | |/ /__\\ | |/ /__\\ 
  _| |_   | \__. | | \__/ |_/ /   \ \_  | |  | || \__., | || \__., 
  |_____|   '.__.'  | ;.__/|____| |____|[___][___]'.__.'[___]'.__.' 
                  [__|                                             
  """)
  print("PopAllele Version: 1.0")
  
  parser = argparse.ArgumentParser()


  # Command to generate QR codes from a CSV file
  parser.add_argument('--QRd', dest='csv_file', help='Generate QR codes from a CSV file')

  # Command to generate QR codes from an image
  parser.add_argument('--QRe', dest='qr_code_image', help='Generate QR codes from a QR code image')

  args = parser.parse_args()

  if args.csv_file:
      try:
          marker, lines = genotyping_data(args.csv_file)
          qrdecoding(marker, lines)
          encode_qr("combined_qr_code.png")
          print("QR codes generated successfully.")
      except Exception as e:
          print(f"Error: {e}")

  elif args.qr_code_image:
      try:
          # Add your logic for processing QR code images here
          pass
      except Exception as e:
          print(f"Error: {e}")

  else:
      print("Please provide a valid command. Use -h or --help for more information.")

if __name__ == "__main__":
    main()
