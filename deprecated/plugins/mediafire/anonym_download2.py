#python libs
import urllib, urllib2, httplib, socket
import cookielib
import logging
logger = logging.getLogger(__name__) #__name___ = nombre del modulo. logging.getLogger = Usa la misma instancia de clase (del starter.py).

#Libs
from link_checker import LinkChecker
from core.plugins_core import PluginsCore
from core.network.connection import URLOpen, URLClose #leer/abrir urls. And close connection if except raises.
from addons.captcha.recaptcha import Recaptcha


BASE_URL = "http://mediafire.com"


class FileLinkFoundException(Exception): pass
class PostCaptchaException(Exception): pass
class CaptchaException(Exception): pass
class LimitExceededException(Exception): pass
class LinkNotFoundException(Exception): pass


class AnonymDownload(PluginsCore):
    """"""
    def __init__(self, *args, **kwargs):
        PluginsCore.__init__(self, *args, **kwargs)
    
    def add(self):
        """"""
        try:
            link_file = None
            err_msg = None
            source = None
            res = ""
            pkr = ""
            cookie = cookielib.CookieJar()
            form = None
            max_retries = 3
            
            for retry in range(max_retries + 1):
                try:
                    #First encrypted page.
                    with URLClose(URLOpen(cookie).open(self.link, form)) as s:
                        if self.wait_func():
                            return self.link, None, err_msg
                        s_lines = s.readlines()
                        for line in s_lines:
                            #Get pKr
                            if "pKr='" in line:
                                pkr = line.split("'")[1].split("'")[0]
                            #Get the last block to unescape
                            if "unescape" in line:
                                tmp = line.split("break;}")[-1]
                                tmp = self.split_eval(tmp)
                                
                                #Eval the block until it's plain text
                                res = self.decrypt(tmp)
                            #Recaptcha
                            if "challenge?k=" in line:
                                if retry < (max_retries + 1):
                                    recaptcha_key = line.split("challenge?k=")[-1].split('"')[0]
                                    recaptcha_link = "http://www.google.com/recaptcha/api/challenge?k=%s" % recaptcha_key
                                    c = Recaptcha(BASE_URL, recaptcha_link, self.wait_func)
                                    challenge, response = c.solve_captcha()
                                    if response is not None:
                                        #Submit the input to the recaptcha system
                                        form = urllib.urlencode([("recaptcha_challenge_field", challenge), ("recaptcha_response_field", response), ("downloadp", "")])
                                        raise PostCaptchaException("Post captcha solution")
                                    else:
                                        raise CaptchaException("No response from the user")
                                else:
                                    raise CaptchaException("Captcha, max retries reached")
                    
                    id_func = res.split("(")[0] #Name of the function containig the id refering to the div that contains the real link
                    
                    pk1 = res.split("'")[3].split("'")[0]
                    qk = res.split("'")[1].split("'")[0] #Public ID of the file
                    
                    for line in s_lines:
                        #Line containing the function to parse
                        if id_func in line:
                            #Try to get the crypted block
                            try:
                                tmp = line.split(id_func)[1].split("setTimeout")[0].split('"none";')[1]
                                tmp = self.split_eval(tmp)
                            except Exception as err:
                                print line
                                raise

                            #Decrypt until it's plain text
                            res = self.decrypt(tmp)

                    div_id = res.split('getElementById("')[1].split('"')[0]

                    data = urllib.urlencode([("qk",qk), ("pk1", pk1), ("r", pkr),])

                    form_action = "http://www.mediafire.com/dynamic/download.php?%s" % data
                except PostCaptchaException as err:
                    pass
                else:
                    break
            
            try:
                #Second encrypted page.
                with URLClose(URLOpen(cookie).open(form_action)) as s:
                    if self.wait_func():
                        return self.link, None, err_msg
                    s_lines = s.readlines()
                    for line in s_lines: #s_lines[1:] we dont care about the first line
                        #print "NEW " + line
                        #Table with the real and fakes dl var.
                        if "function dz()" in line:
                            #Decrypt the table containig the final dl var
                            tmp = line.split("break;")[0].split("eval(")
                            for t in tmp:
                                if "unescape" in t:
                                    t = t.replace("\\","")
                                    table = self.decrypt(t)
                        #Result is plain text (small files) not working.
                        if "http://download" in line:
                            #Get all the dl links (even the fake ones)
                            var = line.split('mediafire.com/" +')
                            #Get the number of the server
                            serv = line.split("http://download")[1].split(".")[0] #error toma otra cosa
                            #Get the name of the file
                            name = var[1].split('+')[1].split("/")[2].split('"')[0].strip("\\")
                            #Find the real link among the fake ones
                            it = iter(var)
                            for tmp in it:
                                #Real link
                                if div_id in tmp:
                                    tmp = it.next()
                                    tmp = tmp.split('+')[0]
                                    #Get the final dl var in the table
                                    dl = table.split(tmp+"=")[1].split(";")[0].strip("'")
                            raise FileLinkFoundException()
                        #Result is encrypted
                        else:
                            tmp = line.split("=''")[-1]
                            tmp = tmp.split("eval(")
                            #Decrypt until the real link is found
                            for t in tmp:
                                if "unescape" in t:
                                    t = t.replace("\\","")
                                    t = t.split("=''")[-1]
                                    res = self.decrypt(t, div_id)
                                    if len(res) == 3:
                                        serv = res[0]
                                        var = res[1]
                                        name = res[2]
                                        raise FileLinkFoundException()
                #if we get here, the link was not found.
                raise LinkNotFoundException("Link not found")
            except FileLinkFoundException as err:
                pass
            
            dl = table.split(var+"=")[1].split(";")[0].strip("'")
            link_file = "http://%s/%sg/%s/%s" % (serv, dl, qk, name)
            
            with URLClose(URLOpen(cookie).open(link_file, range=(self.content_range, None)), always_close=False) as s:
                source = s
            print link_file
        except (urllib2.URLError, httplib.HTTPException, socket.error) as err:
            print err
            err_msg = err
        except (CaptchaException, LinkNotFoundException) as err:
            print err
            err_msg = err
            logging.exception(err)
        except Exception as err:
            err_msg = err
            print err
            logging.exception(err)
        
        return self.link, source, err_msg #puede ser el objeto archivo o None.

    def split_eval(self, tmp):
        res = tmp.replace("\\","")
        res = res.split("=''")[-1]
        res = res.split("eval(")[0]
        return res

    def decrypt(self, tmp, div=None):
        for j in range(10):
            res = ""
            try:
                bond = tmp.split("');")[1].split(";")[0].split("=")[-1]
            except:
                return []
            coef = tmp.split(")^")[1]
            coef = coef.split(")")[0]
            coef = coef.split("^")
            esc = urllib.unquote(tmp.split("unescape('")[1].split("');")[0])
            for i in range(int(bond)):
                ordt = int(esc[i*2:i*2+2], 16) #mi6ib4pvsjx.substr(i * 2, 2), 16)^4^6^8)
                for a in coef:
                    ordt = ordt^int(a)
                res = "%s%s" %(res,chr(ordt))
            
            #When the second request is encrypted.
            #Find the real link among the fake ones.
            if div:
                if div in res: #parent.document.getElementById('...div...')
                    #sometimes it's an IP, sometimes a domain.
                    serv = res.split("http://")[1].split("/")[0]
                    var = res.split('" +')[1].split("+")[0]
                    name = "g/".join(res.split('g/')[1:]).split("\\")[0].split("/")[1]
                    return [serv, var, name]

            #Plain text
            if "unescape" not in res:
                return res
            else:
                tmp = self.split_eval(res)

    def check_link(self, link):
            """"""
            return LinkChecker().check(link)

if __name__ == "__main__":

    def wait_func(some=None):
        return False
    def set_limit_exceeded():
        pass
    
    link = "http://www.mediafire.com/?0kp95lwjtz5qwf2"
    content_range = None
    AnonymDownload(link, content_range, wait_func=wait_func, set_limit_exceeded=set_limit_exceeded).add()
    #print AnonymDownload(link, content_range, wait_func=wait_func, set_limit_exceeded=set_limit_exceeded).check_links(link)
    
    