import utils
import Statistics
import Article

# Grep articles from services and extract informations
# Used to debug services

if __name__ == "__main__":

    if len(sys.argv) < 4 :
        print("Please use # python beattest.py settings.xml services.xml service")
        sys.exit(1)
    else :
        settings = utils.utils.loadxml(sys.argv[1])
        services = utils.utils.loadxml(sys.argv[2])

        debug = settings.find('settings').find('debug').text
        if debug : print("+-[Debug ON]")
