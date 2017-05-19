import json
import time

from channels import Group
from channels.auth import channel_session_user, channel_session_user_from_http

from django.utils.html import escape


@channel_session_user_from_http
def ws_connect(message):
	if message.user.username:
		Group('users').add(message.reply_channel)
		Group('users').send({
			'text': json.dumps({
				'username': message.user.username,
				'is_logged_in': True
			})
		})


@channel_session_user
def ws_disconnect(message):
	if message.user.username:
		Group('users').send({
			'text': json.dumps({
				'username': message.user.username,
				'is_logged_in': False
			})
		})
		Group('users').discard(message.reply_channel)


@channel_session_user
def ws_post(message):
	template_message = '<div class="row">\
		<div class="col-xs-10 col-xs-offset-1 col-sm-10 col-sm-offset-1 col-md-10 col-md-offset-1 col-lg-10 col-lg-offset-1">\
			<p>\
				<b>{0}</b><small class="pull-right time"><i class="fa fa-clock-o"></i>{1}</small>\
				<p>{2}</p>\
			</p>\
		</div>\
	</div>\
	<hr>'.format(message.user.username, time.ctime(), escape(message['text']))

	Group('users').send({
		'text': json.dumps({
			'message': template_message,
		})
	})
