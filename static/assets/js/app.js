// (c) Paul Irish
UTIL = {
  fire : function(func,funcname, args){
    var namespace = Movesol;  // indicate your obj literal namespace here
    funcname = (funcname === undefined) ? 'init' : funcname;
    if (func !== '' && namespace[func] && typeof namespace[func][funcname] == 'function'){
      namespace[func][funcname](args);
    }

  },

  loadEvents : function(){
    var bodyId = document.body.id;
    UTIL.fire('common');
    $.each(document.body.className.split(/\s+/),function(i,classnm){
      UTIL.fire(classnm);
      UTIL.fire(classnm,bodyId);
    });
    UTIL.fire('common','finalize');
  }
};

// Site-specific

Helpers = {
	getTaskCommission: function(task_price) {
		return Math.floor(task_price * GLOBAL.config.payments.commission_coeff);
	}
};

Movesol = {
	common: {
		init: function() {
			$(document).foundation();
			$.datetimepicker.setLocale('ru');
			$('.datetime').datetimepicker({
				format: 'd.m.Y H:i',
				minDate: '0',
                dayOfWeekStart: 1
			});
			$('.wysiwyg').trumbowyg({
				lang: 'ru',
				autogrow: false,
				resetCss: true,
                btnsAdd: ['upload']
			});
            /*tinymce.init({
                selector: '.wysiwyg',
                plugins: 'image media',
                menubar: false,
                language: 'ru',
                image_upload_url: 'api/v1/wysiwyg_uploads/',
                automatic_uploads: true
            });*/
		}
	},
    
    admin_info: {
        init: function() {
            
            $('[data-action="delete"]').on('click', function() {
                var $this = $(this);
                var id = $this.attr('data-id');
                $.ajax({
                    method: 'DELETE',
                    url: '/api/v1/info/' + id + '/',
                    error: function(xhr, textStatus, errorThrown) {
                        console.log(textStatus + '\n' + errorThrown + '\n' + xhr.responseText);
                    },
                    success: function(response) {
                        window.location.reload();
                    }
                });
            });
            
        }
    },
    
    request_doer_rights: {
        init: function() {
            $('.js-action-add-trusted').on('click', function() {
				var $this = $(this);
				var $form = $(
					'<div class="popup">' + 
					'<h3>Добавление доверенного лица</h3>' + 
					'<ul class="errors-list"></ul>' + 

					'<label>ФИО</label>' +
					'<input type="text" name="full_name" value="">' +
                    '<label>Телефон</label>' +
					'<input type="text" name="phone" value="">' +
                    '<label>Комментарий</label>' +
                    '<p>Кем вам приходится этот человек?</p>' +
					'<textarea name="description"></textarea>' +
			
					'<a class="button js-button-apply">Сохранить</a>' + 
					'<a class="button js-button-cancel">Отмена</a>' + 
					'</div>'
				);


				$form.find('.js-button-apply').on('click', function() {
					var data = {
						'full_name': $form.find('[name="full_name"]').first().val(),
						'phone': $form.find('[name="phone"]').first().val(),
						'description': $form.find('[name="description"]').first().val()
					};

					var data_json = JSON.stringify(data);

					$.ajax({
						method: 'POST',
						url: '/api/v1/trusted_persons/',
						contentType: 'application/json',
						data: data_json,
						error: function(xhr, textStatus, errorThrown) {
							console.log(textStatus + '\n' + errorThrown + '\n' + xhr.responseText);
						},
						success: function(response) {
							//window.location.href = '/users/' + GLOBAL.current_user.id + '';
                            console.log(response);
                            $('.trusted-persons').append(
                                '<tr>' + 
                                '<td>' + data.full_name + '</td>' +
                                '<td>' + data.phone + '</td>' +
                                '<td>' + data.description + '</td>' +
                                '<td><a class="button tiny js-button-delete-trusted" data-id="' + response.id + '">Удалить</a></td>' +
                                '</tr>'
                            );
                            console.log($('.trusted-persons > tr').length);
                            if ($('.trusted-persons tr').length > 1) { $('.trusted-persons').show() }
                            if ($('.trusted-persons tr').length > 2) { $('.js-action-add-trusted').hide(); }
                            $.magnificPopup.close();
						}
					});

				});

				$form.find('.js-button-cancel').on('click', function() {
					$form.find('.editor').val(''); // unnecessary?
					$.magnificPopup.close();
				});


				$.magnificPopup.open({items: {src: $form}});
			});
            
            $('body').on('click', '.js-button-delete-trusted', function() {
				var $this = $(this);
                
                $.ajax({
                    method: 'DELETE',
                    url: '/api/v1/trusted_person/' + $this.attr('data-id') + '/',
                    error: function(xhr, textStatus, errorThrown) {
                        console.log('error ob delete');
                        console.log(textStatus + '\n' + errorThrown + '\n' + xhr.responseText);
                    },
                    success: function(response) {
                        //console.log(response);
                        //window.location.href = '/users/' + GLOBAL.current_user.id;
                        $this.closest('tr').remove();
                        console.log($('.trusted-persons tr').length);
                        if ($('.trusted-persons tr').length === 1) { $('.trusted-persons').hide() }
                        if ($('.trusted-persons tr').length < 3) { $('.js-action-add-trusted').show(); }
                    }
                });
			});
            
            $('.js-action-edit-task-cats').on('click', function() {
				var $this = $(this);
				var cats_html = '';

				for (var i = 0; i < GLOBAL.all_categories.length; ++i) {
					var cat = GLOBAL.all_categories[i];
					cats_html += '<optgroup label="' + cat.name + '">';
					for (var j = 0; j < cat.children.length; ++j) {
						var subcat = cat.children[j];
						cats_html += '<option ' + (subcat.done_by_this_user ? 'selected="selected"' : '') + ' value="' + subcat.id + '">' + subcat.name + '</option>';
					}
					cats_html += '</optgroup>';
				} 

				var $form = $(
					'<div class="popup">' + 
					'<h3>Выберите категории заданий, которые вы хотели бы выполнять</h3>' + 
					'<ul class="errors-list"></ul>' + 
					'<select class="js-cats-list" multiple data-placeholder="Добавьте категории...">' +
					cats_html +
					'</select>' +
					'<a class="button js-button-apply">Применить</a>' + 
					'<a class="button js-button-cancel">Отмена</a>' + 
					'</div>'
				);

				$form.find('.js-cats-list').chosen({max_selected_options: 3});

				$form.find('.js-button-apply').on('click', function() {
					var data = {
						'task_categories': $form.find('.js-cats-list').first().val() || []
					};

					var data_json = JSON.stringify(data);

					$.ajax({
						method: 'PUT',
						url: '/api/v1/users/' + GLOBAL.current_user.id + '/',
						contentType: 'application/json',
						data: data_json,
						error: function(xhr, textStatus, errorThrown) {
							console.log(textStatus + '\n' + errorThrown + '\n' + xhr.responseText);
						},
						success: function(response) {
							//console.log(response);
							//window.location.href = '/users/' + GLOBAL.current_user.id + '/';
                            $('.task-categories').empty();
                            for (var i = 0; i < response.task_categories.length; ++i) {
                                $('.task-categories').append('<li>' + response.task_categories[i].name + '</li>');
                            }
                            $.magnificPopup.close();
						}
					});

				});

				$form.find('.js-button-cancel').on('click', function() {
					$form.find('.editor').val(''); // unnecessary?
					$.magnificPopup.close();
				});


				$.magnificPopup.open({items: {src: $form}});
			});
            
        }
    },
	
	task_view: {
		init: function() {

			/*
			*	Добавление комментариев
			*/
			$('.js-button-add-comment').on('click', function() {
				var $form = $(
					'<div class="popup">' + 
					'<h2>Напишите комментарий</h2>' + 
					'<ul class="errors-list"></ul>' + 
					'<textarea class="editor"></textarea>' +
					'<a class="button js-button-send">Отправить</a>' + 
					'<a class="button js-button-cancel">Отмена</a>' + 
					'</div>'
				);
				
				$form.find('.js-button-cancel').on('click', function() {
					$form.find('.editor').val('');
					$.magnificPopup.close();
				});
				
				$form.find('.js-button-send').on('click', function() {
					if ($(this).is('[disabled]')) { return false; }
					var data = {
						task_id: GLOBAL.task.id,
						text: $form.find('.editor').first().val()	
					};
					var data_json = JSON.stringify(data);

					$.ajax({
						method: 'POST',
						url: '/api/v1/task_comments/',
						contentType: 'application/json',
						data: data_json,
						error: function(xhr, textStatus, errorThrown) {
							console.log(textStatus + '\n' + errorThrown + '\n' + xhr.responseText);
						},
						success: function(response) {
							window.location.href = '/tasks/' + GLOBAL.task.id + '/';
						}
					});

				});
				
				$.magnificPopup.open({items: {src: $form}});
			});

			/*
			*	Добавление предложений
			*/
			$('.js-button-add-offer').on('click', function() {
				var price_html = '';
				var predefined_price = GLOBAL.task.reward != null;
				if (predefined_price) {
					price_html = '<input class="editor js-price" type="text" disabled="disabled" value="' + GLOBAL.task.reward.toString() + '">';
				} else {
					price_html = '<input class="editor js-price" type="text" data-field="price">';
				}
				var $form = $(
					'<div class="popup">' + 
					'<p>Укажите цену в рублях, за которую вы готовы выполнить это задание. Если хотите, напишите две-три фразы о том, почему заказчику стоит выбрать именно вас.</p>' + 
					'<p>Если заказчик выберет ваше предложение, мы поможем вам связаться друг с другом.</p>' + 
					'<ul class="errors-list"></ul>' + 
					'<div class="row collapse">' +
						'<label>Цена' + (predefined_price ? ' (определена заказчиком)' : '') + '</label>' + 
						'<div class="small-9 columns">' + price_html + '</div>' +
						'<div class="small-3 columns"><span class="postfix">руб.</span></div>' +
					'</div>' + 
					'<p>Комиссия: <span class="js-commission">0</span> руб.</p>' +
					'<p>Ваша прибыль: <span class="js-profit">0</span> руб.</p>' +
					'<p class="error-message js-poor-balance"></p>' +
					'<label>Текст</label>' +
					'<textarea class="editor" data-field="text"></textarea>' +
					'<a class="button js-button-send">Отправить</a>' + 
					'<a class="button js-button-cancel">Отмена</a>' + 
					'</div>'
				);

				$commission = $form.find('.js-commission');
				$profit = $form.find('.js-profit');
				$form.find('.js-price').on('input change', function() {
					var price = parseInt($(this).val());
					var commission = Helpers.getTaskCommission( price );
					$commission.html(commission);
					$profit.html(price - commission);

					if (commission > GLOBAL.current_user.balance) {
						var poor_balance_msg = 'У вас недостаточно средств на счёте для снятия комиссии. ';
						var shortage = commission - GLOBAL.current_user.balance;
						if (GLOBAL.task.reward) {
							poor_balance_msg += 'Пожалуйста, <a href="#">пополните счёт</a> как минимум на ' + shortage + ' руб. или выберите другое, более дешёвое задание.';
						} else {
							poor_balance_msg += 'Пожалуйста, <a href="#">пополните счёт</a> как минимум на ' + shortage + ' руб., снизьте цену или выберите другое, более дешёвое задание.';
						}
						$form.find('.js-poor-balance').html(poor_balance_msg);
						$form.find('.js-button-send').attr('disabled', 'disabled');
					} else {
						$form.find('.js-button-send').removeAttr('disabled');
					}

				});
				$form.find('.js-price').trigger('change');
				
				$form.find('.js-button-cancel').on('click', function() {
					$form.find('.editor').val('');
					$.magnificPopup.close();
				});
				
				$form.find('.js-button-send').on('click', function() {
					if ($(this).is('[disabled]')) { return false; }

					var data = {
						task_id: GLOBAL.task.id,
						text: $form.find('[data-field="text"]').first().val()
					};
					if (GLOBAL.task.reward == null) {
						data.price = $form.find('[data-field="price"]').first().val();
					}
					var data_json = JSON.stringify(data);

					$.ajax({
						method: 'POST',
						url: '/api/v1/task_offers/',
						contentType: 'application/json',
						data: data_json,
						error: function(xhr, textStatus, errorThrown) {
							console.log(textStatus + '\n' + errorThrown + '\n' + xhr.responseText);
						},
						success: function(response) {
							window.location.href = '/tasks/' + GLOBAL.task.id + '/';
						}
					});

				});
				
				$.magnificPopup.open({items: {src: $form}});
			});


			/*
			*	Подтверждение выполнения
			*/
			$('.js-action-confirm-execution').on('click', function() {
				var $form = $(
					'<div class="popup">' + 
					'<p>Оставьте короткий отзыв ' + (GLOBAL.task.customer.id === GLOBAL.current_user.id ? 'об исполнителе' : 'о заказчике' ) + '</p>' + 
					'<ul class="errors-list"></ul>' + 
					'<label>Текст</label>' +
					'<textarea class="editor" data-field="text"></textarea>' +
					'<p>Поставьте оценку ' + (GLOBAL.task.customer.id === GLOBAL.current_user.id ? 'исполнител.' : 'заказчику' ) + '</p>' +
					'<select data-field="rating">' +
						'<option value="5" selected="selected">Отлично</option>' + 
						'<option value="4">Хорошо</option>' + 
						'<option value="3">Нормально</option>' + 
						'<option value="2">Так себе</option>' + 
						'<option value="1">Плохо</option>' +
					'</select>' +
					'<a class="button js-button-send">Отправить</a>' + 
					'<a class="button js-button-cancel">Отмена</a>' + 
					'</div>'
				);
				
				$form.find('.js-button-cancel').on('click', function() {
					$form.find('.editor').val('');
					$.magnificPopup.close();
				});
				
				$form.find('.js-button-send').on('click', function() {
					if ($(this).is('[disabled]')) { return false; }

					var data = {
						task_id: GLOBAL.task.id,
						text: $form.find('[data-field="text"]').first().val(),
						rating: $form.find('[data-field="rating"]').first().val()
					};

					var data_json = JSON.stringify(data);

					$.ajax({
						method: 'POST',
						url: '/api/v1/task_confirmations/',
						contentType: 'application/json',
						data: data_json,
						error: function(xhr, textStatus, errorThrown) {
							console.log(textStatus + '\n' + errorThrown + '\n' + xhr.responseText);
						},
						success: function(response) {
							window.location.href = '/tasks/' + GLOBAL.task.id + '/';
						}
					});

				});
				
				$.magnificPopup.open({items: {src: $form}});
			});

			/*
			*  Отмена своего предложения
			*/
			$('.js-action-remove-own-offer').on('click', function() {
				$.ajax({
					method: 'DELETE',
					url: '/api/v1/task_offers/' + $(this).attr('data-id') + '/',
					error: function(xhr, textStatus, errorThrown) {
						console.log(textStatus + '\n' + errorThrown + '\n' + xhr.responseText);
					},
					success: function(response) {
						window.location.href = '/tasks/' + GLOBAL.task.id + '/';
					}
				});
			});	

			/*
			* Принятие предложения
			*/
			$('.js-action-accept-offer').on('click', function() {
				$this = $(this);
				$.ajax({
					method: 'POST',
					url: '/api/v1/task_offer_confirmations/',
					contentType: 'application/json',
					data: JSON.stringify( {offer_id: $this.attr('data-offer-id')} ),
					error: function(xhr, textStatus, errorThrown) {
						console.log(textStatus + '\n' + errorThrown + '\n' + xhr.responseText);
					},
					success: function(response) {
						window.location.href = '/tasks/' + GLOBAL.task.id + '/';
					}
				});
			});

			/*
			*  Удаление задания; TODO: сообщение об успешном удалении
			*/
			$('.js-action-remove-task').on('click', function() {
				$.ajax({
					method: 'DELETE',
					url: '/api/v1/tasks/' + $(this).attr('data-id') + '/',
					error: function(xhr, textStatus, errorThrown) {
						console.log(textStatus + '\n' + errorThrown + '\n' + xhr.responseText);
					},
					success: function(response) {
						window.location.href = '/tasks/';
					}
				});
			});	




		}	
	},

	user_profile: {
		init: function() {
            $('.js-mfp').magnificPopup({type:'image'});
            
			$('.js-action-edit-task-cats').on('click', function() {
				var $this = $(this);
				var cats_html = '';

				for (var i = 0; i < GLOBAL.all_categories.length; ++i) {
					var cat = GLOBAL.all_categories[i];
					cats_html += '<optgroup label="' + cat.name + '">';
					for (var j = 0; j < cat.children.length; ++j) {
						var subcat = cat.children[j];
						cats_html += '<option ' + (subcat.done_by_this_user ? 'selected="selected"' : '') + ' value="' + subcat.id + '">' + subcat.name + '</option>';
					}
					cats_html += '</optgroup>';
				} 

				var $form = $(
					'<div class="popup">' + 
					'<h3>Выберите категории заданий, которые вы хотели бы выполнять</h3>' + 
					'<ul class="errors-list"></ul>' + 
					'<select class="js-cats-list" multiple data-placeholder="Добавьте категории...">' +
					cats_html +
					'</select>' +
					'<a class="button js-button-apply">Применить</a>' + 
					'<a class="button js-button-cancel">Отмена</a>' + 
					'</div>'
				);

				$form.find('.js-cats-list').chosen();

				$form.find('.js-button-apply').on('click', function() {
					var data = {
						'task_categories': $form.find('.js-cats-list').first().val() || []
					};

					var data_json = JSON.stringify(data);

					$.ajax({
						method: 'PUT',
						url: '/api/v1/users/' + GLOBAL.current_user.id + '/',
						contentType: 'application/json',
						data: data_json,
						error: function(xhr, textStatus, errorThrown) {
							console.log(textStatus + '\n' + errorThrown + '\n' + xhr.responseText);
						},
						success: function(response) {
							//console.log(response);
							window.location.href = '/users/' + GLOBAL.current_user.id + '/';
						}
					});

				});

				$form.find('.js-button-cancel').on('click', function() {
					$form.find('.editor').val(''); // unnecessary?
					$.magnificPopup.close();
				});


				$.magnificPopup.open({items: {src: $form}});
			});

			$('.js-action-change-password').on('click', function() {
				var $this = $(this);

				var $form = $(
					'<div class="popup">' + 
					'<h3>Смена пароля</h3>' + 
					'<ul class="errors-list"></ul>' + 

					'<label>Введите ваш действующий пароль</label>' +
					'<input type="password" name="password_old" value="">' +

					'<label>Введите новый пароль</label>' +
					'<input type="password" name="password_new" value="">' +

					'<a class="button js-button-apply">Применить</a>' + 
					'<a class="button js-button-cancel">Отмена</a>' + 
					'</div>'
				);


				$form.find('.js-button-apply').on('click', function() {
					var data = {
						'password_old': $form.find('[name="password_old"]').first().val(),
						'password_new': $form.find('[name="password_new"]').first().val()
					};

					var data_json = JSON.stringify(data);

					$.ajax({
						method: 'POST',
						url: '/api/v1/users/' + GLOBAL.current_user.id + '/password_change/',
						contentType: 'application/json',
						data: data_json,
						error: function(xhr, textStatus, errorThrown) {
							console.log(textStatus + '\n' + errorThrown + '\n' + xhr.responseText);
						},
						success: function(response) {
							//console.log(response);
							window.location.href = '/users/' + GLOBAL.current_user.id + '';
						}
					});

				});

				$form.find('.js-button-cancel').on('click', function() {
					$form.find('.editor').val(''); // unnecessary?
					$.magnificPopup.close();
				});


				$.magnificPopup.open({items: {src: $form}});
			});
            
            $('.js-action-add-trusted').on('click', function() {
				var $this = $(this);
				var $form = $(
					'<div class="popup">' + 
					'<h3>Добавление доверенного лица</h3>' + 
					'<ul class="errors-list"></ul>' + 

					'<label>ФИО</label>' +
					'<input type="text" name="full_name" value="">' +
                    '<label>Телефон</label>' +
					'<input type="text" name="phone" value="">' +
                    '<label>Комментарий</label>' +
                    '<p>Кем вам приходится этот человек?</p>' +
					'<textarea name="description"></textarea>' +
			
					'<a class="button js-button-apply">Сохранить</a>' + 
					'<a class="button js-button-cancel">Отмена</a>' + 
					'</div>'
				);


				$form.find('.js-button-apply').on('click', function() {
					var data = {
						'full_name': $form.find('[name="full_name"]').first().val(),
						'phone': $form.find('[name="phone"]').first().val(),
						'description': $form.find('[name="description"]').first().val()
					};

					var data_json = JSON.stringify(data);

					$.ajax({
						method: 'POST',
						url: '/api/v1/trusted_persons/',
						contentType: 'application/json',
						data: data_json,
						error: function(xhr, textStatus, errorThrown) {
							console.log(textStatus + '\n' + errorThrown + '\n' + xhr.responseText);
						},
						success: function(response) {
							window.location.href = '/users/' + GLOBAL.current_user.id + '';
						}
					});

				});

				$form.find('.js-button-cancel').on('click', function() {
					$form.find('.editor').val(''); // unnecessary?
					$.magnificPopup.close();
				});


				$.magnificPopup.open({items: {src: $form}});
			});
            
            $('.js-button-delete-trusted').on('click', function() {
				var $this = $(this);
                
                $.ajax({
                    method: 'DELETE',
                    url: '/api/v1/trusted_person/' + $this.attr('data-id') + '/',
                    error: function(xhr, textStatus, errorThrown) {
                        console.log(textStatus + '\n' + errorThrown + '\n' + xhr.responseText);
                    },
                    success: function(response) {
                        //console.log(response);
                        window.location.href = '/users/' + GLOBAL.current_user.id;
                    }
                });
			});

			$('.js-edit-field').on('click', function() {
				var $this = $(this);
				var field = $this.attr('data-field');
				var msg = $this.attr('data-message') || 'Введите новое значение ' + field + '';
				var converter = $this.attr('data-convert') || 'none';

				var data_edit_type = $this.attr('data-edit-type') || 'text';
				var editor_html = '';
				switch (data_edit_type) {
					case 'text':
						editor_html = '<input class="editor" type="text" data-field="' + field + '">';
						break;
					case 'textarea':
						editor_html = '<textarea class="editor" data-field="' + field + '"></textarea>';
						break;
					default:
						console.log('ERROR: invalid data-edit-type: ' + data_edit_type);
				}

				var $form = $(
					'<div class="popup">' + 
					'<h2>' + msg + '</h2>' + 
					'<ul class="errors-list"></ul>' + 
					editor_html +
					'<a class="button js-button-apply">Применить</a>' + 
					'<a class="button js-button-cancel">Отмена</a>' + 
					'</div>'
				);

				$form.find('.editor').val(GLOBAL.current_user[field]);

				$form.find('.js-button-cancel').on('click', function() {
					$form.find('.editor').val(''); // unnecessary?
					$.magnificPopup.close();
				});

				$form.find('.js-button-apply').on('click', function() {
					var data = {};
					$form.find('.editor').each(function() {
						var $this = $(this);
						if ($this.attr('data-field')) {
							switch (converter) {
								case 'int':
									data[$this.attr('data-field')] = parseInt( $this.val() ); 
									break;
								case 'none':
									data[$this.attr('data-field')] = $this.val(); 
									break;
								default:
									data[$this.attr('data-field')] = $this.val(); 
									break;
							}
						}
					});
					var data_json = JSON.stringify(data);

					$.ajax({
						method: 'PUT',
						url: '/api/v1/users/' + GLOBAL.current_user.id + '/',
						contentType: 'application/json',
						data: data_json,
						error: function(xhr, textStatus, errorThrown) {
							console.log(textStatus + '\n' + errorThrown + '\n' + xhr.responseText);
						},
						success: function(response) {
							//console.log(response);
							window.location.href = '/users/' + GLOBAL.current_user.id + '/';
						}
					});

				});



				$.magnificPopup.open({items: {src: $form}});
			});
		},
	},

	task_new: {
		init: function() {
			/*$('#price-open').on('click', function() {
				$('#reward').removeAttr('disabled');
			});
			$('#price-fixed').on('click', function() {
				$('#reward').attr('disabled', 'disabled');
			});*/
			$('#reward').on('focus click', function() {
				$('#price-fixed').click();
			});

			$('.task-form__add-address-link').on('click', function() {
				$addresses = $(this).parent().find('.task-form__addresses').first();
				$template = $addresses.find('.task-form__address').first();
				var new_node = $template.clone();
				new_node.find('.task-form__remove-address-link').on('click', function() {
					$(this).closest('.task-form__address').remove();
				});
				$addresses.append(new_node);
			});

			$('.task-form__remove-address-link').on('click', function() {
				$(this).closest('.task-form__address').remove();
			});

			$('.task-form__submit').on('click', function(e) {
				e.preventDefault();

				var $form = $('form.task-form');

				var price_open = !!parseInt($('input[name="price-open"]:checked').val());
				var price = price_open ? null : parseInt($form.find('input[name="reward"]').val());

				var addresses = $form.find('.task-form__address .address').map(function() {
					return $(this).val();
				}).get();
				
				var data = JSON.stringify({
						title: 					$form.find('input[name="title"]').first().val(),
						description: 			$form.find('textarea[name="description"]').first().val(),
						category_id: 			$form.find('select[name="category_id"]').first().val(),
						due: 					$form.find('input[name="due"]').first().val(),
						addresses: 				addresses,
						reward: 				price,
						contacts: 				[{'type': 'phone', 'value': $form.find('input[name="phone"]').first().val()}]
					});

				console.log(data);
				$.ajax({
					method: 'POST',
					url: '/api/v1/tasks/',
					contentType: 'application/json',
					data: data,
					error: function(xhr, textStatus, errorThrown) {
						console.log(textStatus + '\n' + errorThrown + '\n' + xhr.responseText);
					},
					success: function(response) {
						//console.log(response);
						window.location.href = '/tasks/' + response.id + '/';
					}
				});
			});

		}
	},

	payment_new: {
		init: function() {
			// Состоит ли строка из цифр
			function isdigit(s) {
			  var digits = '0123456789'.split('');
			  for (var i = 0; i < s.length; ++i) { if (digits.indexOf(s.charAt(i)) < 0) return false; }
			  return true;
			}

			// Фильтрует строку s функцией f
			function filterString(s, f) {
			  var result = '';
			  for (var i = 0; i < s.length; ++i) { if (f(s.charAt(i))) result += s.charAt(i); }
			  return result;
			}

			var sum_field = $('[name=WMI_PAYMENT_AMOUNT]');

			// Приводит сумму к виду XX.00
			function normalizeSumString(str) {
			  return filterString(str.split(/[\,\.]+/ig)[0].trim(), isdigit) + '.00';
			}

			// Изменяет текст поля ввода, сохраняя позицию курсора
			var setSoftly = function(el, text){
			    var start = el.selectionStart,
			        end = el.selectionEnd;
			    $(el).val( text );
			    el.setSelectionRange(start, end);
			};

			// Нормализуем введённую сумму при изменении
			sum_field.on('blur keyup change', function() { 
			  var raw_content = sum_field.val();
			  var content = raw_content;
			  if (content.trim() === '') content = '0';
			  var new_content = normalizeSumString(content);
			  if (content !== new_content) {
			    setSoftly(sum_field[0], new_content);
			  }
			});

			// Для удобства ограничиваем позицию курсора целой частью суммы
			sum_field.on('mousedown mouseup keydown keyup paste focus', function() {
				var content = sum_field.val();
				var assumedDotPos = content.length - 3;
				var actualDotPos = content.indexOf('.');
				var max_pos = Math.max(assumedDotPos, actualDotPos);
				if (sum_field[0].selectionEnd > max_pos) {
					sum_field[0].selectionEnd = max_pos;
				}
			});
		}
	}
};

$(document).ready(UTIL.loadEvents);