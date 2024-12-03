import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import random
from time import sleep

# 请求头
h1 = {
	'Cookie': 'douban-fav-remind=1; __utmv=30149280.24427; _vwo_uuid_v2=D363211F1FC3BB5880394DAC02FA26AF3|fa3eba5dde64d395fffe7b293a51785b; ll="118282"; bid=ILUFQTNIMmE; _pk_id.100001.4cf6=416e6e90278552a9.1721403185.; __yadk_uid=7mjC2WRQAKtq4iyCRICyHUCfsDTP3Ulb; __utma=30149280.1328450298.1625151050.1721984404.1722322438.56; __utmc=30149280; __utmz=30149280.1722322438.56.35.utmcsr=cn.bing.com|utmccn=(referral)|utmcmd=referral|utmcct=/; ap_v=0,6.0; __utma=223695111.199656476.1639326188.1721984404.1722322453.9; __utmb=223695111.0.10.1722322453; __utmc=223695111; __utmz=223695111.1722322453.9.4.utmcsr=douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/search; _pk_ref.100001.4cf6=%5B%22%22%2C%22%22%2C1722322453%2C%22https%3A%2F%2Fwww.douban.com%2Fsearch%3Fq%3D%E7%99%BD%E8%9B%87%E4%BC%A0%2B%E6%83%85%22%5D; _pk_ses.100001.4cf6=1; dbcl2="244279769:fmB2CDuGGho"; ck=gjjF; push_noty_num=0; push_doumail_num=0; __utmt=1; __utmt_douban=1; __utmb=30149280.13.10.1722322438',
	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
	'Accept-Encoding': 'gzip, deflate',
	'Host': 'movie.douban.com',
	'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.4 Safari/605.1.15',
	'Accept-Language': 'zh-CN,zh-Hans;q=0.9',
	'Referer': 'https://movie.douban.com/subject/34825976/?from=showing',
	'Connection': 'keep-alive'
}


# 转换评论星级
def trans_star(v_str):
	v_str = v_str[0]
	if v_str == 'allstar10':
		return '1星'
	elif v_str == 'allstar20':
		return '2星'
	elif v_str == 'allstar30':
		return '3星'
	elif v_str == 'allstar40':
		return '4星'
	elif v_str == 'allstar50':
		return '5星'
	else:
		return '未知'


def get_short(v_movie_id, start_page):
	for page in range(start_page, start_page + max_page):  # 从start_page开始往后爬30页
		requests.packages.urllib3.disable_warnings()
		# 请求地址
		# 最近
		url = 'https://movie.douban.com/subject/{}/comments?start={}&limit=20&status=P&sort=time'.format(v_movie_id, page * 20)
		# 热门-好评
		# url = 'https://movie.douban.com/subject/{}/comments?percent_type=h&start={}&limit=20&status=P&sort=new_score'.format(v_movie_id, page * 20)
		# 热门-一般
		# url = 'https://movie.douban.com/subject/{}/comments?percent_type=m&start={}&limit=20&status=P&sort=new_score'.format(v_movie_id, page * 20)
		# 热门-差评
		# url = 'https://movie.douban.com/subject/{}/comments?percent_type=l&start={}&limit=20&status=P&sort=new_score'.format(v_movie_id, page * 20)
		# 热门
		# url = 'https://movie.douban.com/subject/{}/comments?start={}&limit=20&status=P&sort=new_score'.format(v_movie_id, page * 20)
		
		response = requests.get(url, headers=h1, verify=False)
		print('状态码: ', response.status_code)
		soup = BeautifulSoup(response.text, 'html.parser')
		reviews = soup.find_all('div', {'class': 'comment'})
		print('开始爬取第{}页，共{}条评论'.format(page, len(reviews)))
		sleep(random.uniform(1, 2))
		# 储存数据
		user_name_list = []     # 昵称
		star_list = []          # 星级
		ip_list = []            # ip属地
		content_list = []       # 评论内容
		for review in reviews:
			ip = review.find('span', {'class': 'comment-location'}).text # 只保存有ip信息的
			if ip:
				user_name = review.find('span', {'class': 'comment-info'}).find('a').text
				user_name_list.append(user_name)
				star = review.find('span', {'class': 'comment-info'}).find_all('span')[1].get('class')
				star = trans_star(star)
				star_list.append(star)
				# ip = review.find('span', {'class': 'comment-location'}).text
				ip_list.append(ip)
				content = review.find('span', {'class': 'short'}).text
				content = content.replace(',', '，').replace(' ', '').replace('\n', '').replace('\t', '').replace('\r', '')
				content_list.append(content)
		df = pd.DataFrame(
			{
				'页码': page,
				'评论者': user_name_list,
				'星级': star_list,
				'IP属地': ip_list,
				'评论内容': content_list,
			}
		)

		# 保存到csv文件
		if os.path.exists(result_file):
			header = False
		else:
			header = True
		df.to_csv(result_file, mode='a+', header=header, index=False, encoding='utf_8_sig')
		print('文件保存成功：', result_file)


if __name__ == '__main__':
	# 电影id
	movie_id = '34825976'
	# 起始页
	start_page = 1
	# 最大爬取页
	max_page = 10
	# 保存文件名
	result_file = '豆瓣短评.csv'
	# 循环爬取短评
	get_short(movie_id, start_page)