# -*- coding: utf-8 -*-


def headers_to_dict(block):
    headers = {}
    url = ''
    for line in block.strip().split(' '*2):
        line = line.strip()
        if line.startswith('curl'):
            url = line.split()[-1].strip("'")
        # ['-H \'sec-ch-ua-platform: "macOS"\'']
        if line.startswith('-H'):
            line = line[3:].strip("'")
            k, v = line.split(': ')
            headers[k] = v
    cookie = None
    if 'cookie' in headers:
        cookie = cookie_to_dict(headers['cookie'])

    return url, headers, cookie


def cookie_to_dict(block):
    cookie = {}
    #for line in block.split(': ')[-1].split(';'):
    for line in block.split(';'):
        k, v = line.strip().split('=', 1)
        cookie[k] = v
    return cookie



if __name__ == '__main__':
    block = """
        curl 'https://www.zhihu.com/api/v4/search_v3?gk_version=gz-gaokao&t=general&q=%E6%8A%80%E6%9C%AF%E5%90%88%E4%BC%99%E4%BA%BA%E8%A2%AB%E8%B8%A2%E5%87%BA%E5%B1%80&correction=1&offset=0&limit=20&filter_fields=&lc_idx=0&show_all_topics=0&search_source=Normal' \
  -H 'authority: www.zhihu.com' \
  -H 'accept: */*' \
  -H 'accept-language: zh-CN,zh;q=0.9' \
  -H 'cookie: _xsrf=aBOXMVLHapxph5VZxPN5GkmoZUZAfr5Q; _zap=95dfc6ec-22db-4d08-abe9-2ea7edd52e23; d_c0=AGCWjzAXnBaPTtdd0Fmlj0WDXtWo4yugL_M=|1681212183; YD00517437729195%3AWM_NI=NzcqbRuh1dazZbutBO7IJPrGjuoxD4mR4%2BVm8d7oF2syJWb9ywBe1TEdpHjy0QbOVLoxsTUbU6%2FTXtvRlCGFbsp5HwfTYvEJr%2Fcr8CRJWnP8j7olRvHr%2FRzvDyi7n5wpQU4%3D; YD00517437729195%3AWM_NIKE=9ca17ae2e6ffcda170e2e6eeaab4398eb99fb2ef43a98a8ea7c84e839e8badd85cbaec9bb6e461b086fe8ccd2af0fea7c3b92a8ea6ad92e15ab7b8ff85e4729abebb95c145f59786b1f14daaaba199c740af8efcccd567fcbcf990c53ab1a786b8e133bba98e86b46087bcc0a9e973f48faeb0d548ada8bdb5d86a97eae1b5db80b68ea4a4c64ea2adc0d6cb7da68c9797c842b2f1ad93bb499296998fd334aae9a18dd17e8caee1b3f97e88a7a7d8ed3fb5b09fb6b737e2a3; YD00517437729195%3AWM_TID=gOaOs59Z2k5EEUBVUBLBfysUBOhkcnkM; __snaker__id=5FMzz1WoSmQaFH3V; q_c1=47034cf4939543e0b6adad3814d2bdc4|1681212343000|1681212343000; z_c0=2|1:0|10:1698950945|4:z_c0|80:MS4xOUJISklBQUFBQUFtQUFBQVlBSlZUU0U5TVdheUMyMlQ1M2NQc1RaRGx6ZzB1SXVxdnA0SWhRPT0=|c97f99017c077449bef75cd348373a8ec763a23791b712c4de5e9dd01f100581; Hm_lvt_98beee57fd2ef70ccdd5ca52b9740c49=1698153272,1698236195,1699532768; tst=r; Hm_lpvt_98beee57fd2ef70ccdd5ca52b9740c49=1699761424; KLBRSID=d017ffedd50a8c265f0e648afe355952|1699761424|1699759908' \
  -H 'referer: https://www.zhihu.com/search?q=%E6%8A%80%E6%9C%AF%E5%90%88%E4%BC%99%E4%BA%BA%E8%A2%AB%E8%B8%A2%E5%87%BA%E5%B1%80&type=content' \
  -H 'sec-ch-ua: "Chromium";v="118", "Google Chrome";v="118", "Not=A?Brand";v="99"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "macOS"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-origin' \
  -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36' \
  -H 'x-api-version: 3.0.91' \
  -H 'x-app-za: OS=Web' \
  -H 'x-requested-with: fetch' \
  -H 'x-zse-93: 101_3_3.0' \
  -H 'x-zse-96: 2.0_p9JDAKAqy8eXTY9QT8AGlG0Ct3Nk1yFDZ1OxyUkLpN/HxqTMdZBmmY5YTVzTkpkf' \
  -H 'x-zst-81: 3_2.0VhnTj77m-qofgh3TxTnq2_Qq2LYuDhV80wSL7iUZQ6nxE7Y0m4fBJCHMiqHPD4S1hCS974e1DrNPAQLYlUefii7q26fp2L2ZKgSfnveCgrNOQwXTtM2VcArVQXFP8ukLguk8UGxTACNVEgXT97SM-bgmDqSfqUPT16fq-AXmAgxL-cHT_Tf0kUQKF0ntHRX_h0P1SueLF9tVpDSBtD3YXJ9_hbSLcHVG3COL2T31BDp8gCSM19V0yGxf6wtmF0fzhuCY8DUCFBeB9gO_59OyehCGe_38QeS1H9LmsDrmkRcVrqC0WwpfQGRLrwpVLUC08UNMbLofo4C9rH2mhhgKSLxMuBp1HvHf8_N1IugLNUwOwheLBrOC' \
  --compressed
    """.strip()

    _, headers, cookie = headers_to_dict(block)

    print(headers)

    print('------')
    print(cookie)










