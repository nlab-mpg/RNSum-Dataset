import json
import urllib.request

class GitHubApi:
    UNVERIFY_SSL = True
    BASE_URL = 'https://api.github.com'

    def __init__(self, option={}):
        self.option = option
        if self.UNVERIFY_SSL:
            self.__unverify_ssl()

    def __unverify_ssl(self):
        import ssl
        ssl._create_default_https_context = ssl._create_unverified_context

    def __get_json(self, url, token):
        req = self.__create_request(url, token)
        with urllib.request.urlopen(req) as res:
            json_text = res.read().decode('utf-8')
            json_obj = json.loads(json_text)

            return json_obj

    def __create_request(self, url, token):
        req = urllib.request.Request(url)
        req.add_header('Authorization', 'token ' + token)

        return req

    def get_commits(self, path, token):
        url = self.BASE_URL + '/repos' + path
        return self.__get_json(url, token)

    def get_release(self, repo, release_id, token):
        url = self.BASE_URL + '/repos/' + repo + '/releases/' + release_id
        return self.__get_json(url, token)

    def get_releases(self, repo, token):
        url = self.BASE_URL + '/repos/' + repo + '/releases' + '?per_page=100'
        return self.__get_json(url, token)
