import sys
sys.path.append('/var/www/skyblock')

from skyblock import skyblock as application, init_challenges, load_challenges

init_challenges()
load_challenges()

