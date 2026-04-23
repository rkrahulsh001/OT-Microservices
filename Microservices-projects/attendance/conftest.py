import os
import pytest

# Sabse pehle CONFIG_FILE set karo — kisi bhi import se pehle
os.environ['CONFIG_FILE'] = os.path.join(
    os.path.dirname(__file__), 'config.yaml')
