Notes = window.Notes || {};

(function(exports, $) {
  function Editor() {
    // Store state, such as next and previous page.
    this.state = {};
    this.endpoint = '/api/note/';

    // DOM nodes.
    this.form = $('form#note-form');
    this.content = this.form.find('textarea#content');
    this.reminder = this.form.find('input[name="reminder"]');
    this.cancelEditBtn = this.form.find('a#cancel-edit');
    this.container = $('ul.notes');

    // Bind handlers.
    this.initialize();
  }

  /* Initialization and event handler binding. */
  Editor.prototype.initialize = function() {
    this.container.masonry();
    this.setupForm();
    this.bindArchiveDelete();
    this.bindPagination();
    this.bindSearchHandler();
    var page = 1;
    if (window.location.hash) {
      page = parseInt(window.location.hash.replace('#', ''));
    }
    this.getList(page || 1);
  }

  Editor.prototype.setupForm = function() {
    var self = this;
    this.content.on('keydown', function(e) {
      if (e.ctrlKey && e.keyCode == 13) {
        self.form.submit();
      }
    });
    this.content.focus();
    this.addMarkdownHelpers();
    this.form.submit(function(e) {
      e.preventDefault();
      self.addNote();
    });
    this.cancelEditBtn.on('click', function(e) {
      e.preventDefault();
      self.resetForm();
    });
  }

  Editor.prototype.bindArchiveDelete = function() {
    $('a.delete-note,a.archive-note').on('click', this.changeNote);
  }

  Editor.prototype.bindPagination = function() {
    var self = this;
    var makeHandler = function (key) {
      return function(e) {
        e.preventDefault();
        if ($(this).parent().hasClass('disabled')) return;
        if (key == 'next') {
          page = self.state['page'] + 1;
        } else {
          page = self.state['page'] - 1;
        }
        self.getList(page, self.state['search']);
      }
    }
    $('ul.pager li.next a').on('click', makeHandler('next'));
    $('ul.pager li.previous a').on('click', makeHandler('previous'));
  }

  Editor.prototype.bindSearchHandler = function() {
    var self = this;

    $('form#search-form').on('submit', function(e) {
      e.preventDefault();
      var query = $('input[name="q"]').val();
      self.getList(1, query);
    });
  }

  /* Loading and saving notes. */
  Editor.prototype.getList = function(page, search) {
    var requestData = {},
        self = this,
        url = search ? '/api/note/search/' : '/api/note/';

    this.container.empty();

    if (page) requestData['page'] = page;
    if (search) requestData['query'] = search;

    this.makeRequest(url, 'GET', requestData, function(data) {
      data.objects.reverse();
      $.each(data.objects, function(idx, note) {
        self.addNoteToList(note.rendered);
      });
      imagesLoaded(self.container, function() {
        self.container.masonry('layout');
      });
      self.updatePagination(data);
    });
  }

  Editor.prototype.addNoteToList = function(html) {
    var self = this;
    listElem = $(html);
    listElem.find('a.delete-note,a.archive-note').on('click', function(e) {
      e.preventDefault();
      self.changeNote($(this));
    });
    listElem.find('a.edit-note').on('click', function(e) {
      e.preventDefault();
      self.editNote($(this));
    });
    listElem.find('input[type="checkbox"]').on('change', function(e) {
      self.updateTask($(this));
    });
    listElem.find('img').addClass('img-responsive');
    this.container.prepend(listElem);
    this.container.masonry('prepended', listElem);
  }

  Editor.prototype.updatePagination = function(response) {
    var meta = response.meta;
    window.location.hash = meta.page;
    this.state = {'page': meta.page};
    this.state['hasNext'] = meta.next != '';
    this.state['hasPrevious'] = meta.previous != '';
    this.state['search'] = $('input[name="q"]').val();

    var next = $('ul.pager li.next');
    if (this.state.hasNext) {
      next.removeClass('disabled');
    } else {
      next.addClass('disabled');
    }

    var previous = $('ul.pager li.previous');
    if (this.state.hasPrevious) {
      previous.removeClass('disabled');
    } else {
      previous.addClass('disabled');
    }
  }

  Editor.prototype.addNote = function() {
    if (!this.content.val()) {
      this.content.css('color', '#dd1111');
      return
    }

    var note = {'content': this.content.val()},
        isEdit = this.cancelEditBtn.is(':visible');

    if (this.reminder.is(':visible') && this.reminder.val()) {
      // Fix any bizarre date formats.
      var dateTime = this.reminder.val().replace('T', ' ').split('Z')[0];
      if (dateTime.split(':').length == 2) {
        dateTime = dateTime + ':00';
      }
      note['reminder'] = dateTime;
    }

    var self = this;
    this.content.css('color', '#464545');
    this.makeRequest(this.form.attr('action'), 'POST', note, function(data) {
      self.resetForm();
      if (isEdit) {
        $('div#note-panel-' + data.id).remove();
      }
      self.addNoteToList(data.rendered);
    });
  }

  Editor.prototype.resetForm = function() {
    this.form.attr('action', '/api/note/');
    this.cancelEditBtn.hide();
    this.content.val('').focus();
    this.resetReminder();
  }

  Editor.prototype.resetReminder = function() {
    var now = new Date();
    var pad = function(v) {return ('0' + v).slice(-2);}
    this.reminder.val(
      (now.getYear() + 1900) + '-' +
      pad(now.getMonth() + 1) + '-' +
      pad(now.getDate()) + 'T' +
      pad(now.getHours()) + ':' + '00'
    );
  }

  Editor.prototype.editNote = function(noteLink) {
    var self = this,
        noteId = noteLink.data('note'),
        panel = noteLink.parents('.panel'),
        detailsUrl = noteLink.attr('href') + 'details/';

    self.makeRequest(detailsUrl, 'GET', {}, function(response) {
      self.content.val(response.content);
      if (response.reminder) {
        self.reminder.show();
        self.reminder.val(response.reminder);
      } else {
        self.reminder.hide();
      }
      self.form.attr('action', noteLink.attr('href'));
      self.cancelEditBtn.show();
    });
  }

  Editor.prototype.changeNote = function(noteLink) {
    var noteData = {};
    var panel = noteLink.parents('.panel');
    var self = this;

    panel.removeClass('panel-primary').addClass('panel-danger');
    if (noteLink.hasClass('delete-note')) {
      noteData['status'] = 9
    } else {
      noteData['status'] = 2
    }

    this.makeRequest(noteLink.attr('href'), 'POST', noteData, function(data) {
      panel.remove();
      self.container.masonry();
    });
  }

  Editor.prototype.updateTask = function(elem) {
    /* Read checkbox state. */
    var isFinished = elem.is(':checked');
    var taskId = elem.val();
    var url = '/api/task/' + taskId + '/';

    this.makeRequest(url, 'POST', {'finished': isFinished}, function(data) {
      var label = elem.parent();
      var color = label.css('color');
      label.css('color', '#119911');
      window.setTimeout(function() {label.css('color', color);}, 2000);
    });
  }

  /* Make API request. */
  Editor.prototype.makeRequest = function(url, method, data, callback) {
    if (method == 'GET') {
      $.get(url, data, callback);
    } else {
      $.ajax(url, {
        'contentType': 'application/json; charset=UTF-8',
        'data': JSON.stringify(data),
        'dataType': 'json',
        'success': callback,
        'type': method
      });
    }
  }

  /* Markdown and other editor features. */
  Editor.prototype.addMarkdownHelpers = function() {
    var self = this;
    this.addHelper('indent-left', function(line) {return '    ' + line;});
    this.addHelper('indent-right', function(line) {return line.substring(4);});
    this.addHelper('list', function(line) {return '* ' + line;});
    this.addHelper('bold', function(line) {return '**' + line + '**';});
    this.addHelper('italic', function(line) {return '*' + line + '*';});
    this.addHelper('font', null, function() {
      self.focus().select();
    });
    this.addHelper('time', null, function() {
      self.reminder.toggle();
      if (self.reminder.is(':visible')) {
        self.resetReminder();
      } else {
        self.reminder.val('');
      }
    });
  }

  Editor.prototype.addHelper = function(iconClass, lineHandler, callBack) {
    var link = $('<a>', {'class': 'btn btn-xs'}),
        icon = $('<span>', {'class': 'glyphicon glyphicon-' + iconClass}),
        self = this;

    if (!callBack) {
      callBack = function() {
        self.modifySelection(lineHandler);
      }
    }

    link.on('click', function(e) {
      e.preventDefault();
      callBack();
    });
    link.append(icon);
    this.content.before(link);
  }

  Editor.prototype.modifySelection = function(lineHandler) {
    var selection = this.getSelectedText();
    if (!selection) return;

    var lines = selection.split('\n'),
        result = [];
    for (var i = 0; i < lines.length; i++) {
      result.push(lineHandler(lines[i]));
    }

    this.content.val(
      this.content.val().split(selection).join(result.join('\n'))
    );
  }

  Editor.prototype.getSelectedText = function() {
    var textAreaDOM = this.content[0];
    return this.content.val().substring(
      textAreaDOM.selectionStart,
      textAreaDOM.selectionEnd);
  }

  exports.Editor = Editor;
})(Notes, jQuery);