from django.template.context import RequestContext
from django.shortcuts import render_to_response as django_render , redirect
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from django.core.exceptions import ImproperlyConfigured
from UserDict import DictMixin
from django.views.generic import create_update
from django.template.defaultfilters import slugify, random
from django.core import serializers
import random
import json

import time
import math
from urlparse import urljoin
from django.utils.encoding import iri_to_uri
def render_to_response(template,context,request):
    """
        Wrapper to django's render_to_response, with a request context
    """
    return django_render(template,context_instance=RequestContext(request, context))

def render_to_json(context):
    return HttpResponse(json.dumps(context))
CAPS = range(ord('A'),ord('Z')+1)
SMALL =range(ord('a'),ord('z')+1)
NUMS = range(0,10)
CHOICES = CAPS+SMALL+NUMS

def random_name():
    name=[random.choice(CHOICES),random.choice(CHOICES),random.choice(CHOICES),random.choice(CHOICES),random.choice(CHOICES),random.choice(CHOICES)]
    return "".join([to_str(n) for n in name])

def to_str(n):
    if n<10:return str(n)
    return chr(n)
def success_json(message,extra_context=None):
    context={'type':'success','message':message}
    if extra_context:
        context.update(extra_context)
    return HttpResponse(json.dumps(context))

def error_json(global_errors,form_errors=None,extra_context=None):
    context={'type':'error','errors':{'global_errors':global_errors}}
    if extra_context:context.update(extra_context)
    if form_errors:context['errors']['form_errors']=form_errors
    return HttpResponse(json.dumps(context))
 
def formatted_name(user):
    if not user : return ""
    if user.first_name or user.last_name:return user.first_name + " " +user.last_name
    return user.username

def process_and_redirect(form_class,request,template_name, redirect_to,processor,success_msg=_('Your request was processed successfully')):
    form=form_class()
    results={}
    if request.method=='POST':
        form = form_class(request.POST,request.FILES)
        if form.is_valid():
            try:
                results=processor(request,form)
                request.flash['message']=success_msg
                return redirect(redirect_to)
            except ValidationException, e:
                request.flash['message']=" ".join(e.errors)
    results['form']=form
    return render_to_response(template_name, results, request)

def ajax_post_process(form_class,request, template_name=None,processor= lambda r,f,extra:{'instance':f.save()},success_msg=_('Your request was processed successfully'),extra_context=None):
    context={}
    result = None
    if request.method=='GET': 
        context['form']=form_class()
        if extra_context: context.update(extra_context)
        if template_name:return render_to_response(template_name, context, request)
        else: return render_to_json(context)
    post_values=request.POST.copy()
    if extra_context:post_values.update(extra_context)
    form = form_class(post_values,request.FILES)
    message=''
    if form.is_valid():
        try:
            result = processor(request,form,extra_context)
            return success_json(success_msg,result)
        except ValidationException, e:
            message=" ".join(e.errors)
    return error_json([message], {'form':form.errors})

def edit_and_redirect(form_instance,form_class,request,template_name, redirect_to,processor,success_msg=_('Your request was processed successfully')):
    form=form_instance
    results={}
    if request.method=='POST':
        form = form_class(request.POST,request.FILES)
        if form.is_valid():
            try:
                results=processor(request,form)
                request.flash['message']=success_msg
                return redirect(redirect_to)
            except ValidationException, e:
                request.flash['message']=e.errors
    results['form']=form
    return render_to_response(template_name, results, request)

def save_and_redirect(form_class,request,template_name, redirect_to,success_msg=_('Your request was processed successfully')):
    def save(request,form):
        instance=form.save()
        return locals()
    return process_and_redirect(form_class,request,template_name,redirect_to,save,success_msg)

def save_form(form_class,request):
    form=form_class()
    if request.method=='POST':
        form = form_class(request.POST,request.FILES)
        if form.is_valid():
            try:
                instance=form.save()
                return (form,instance,[])
            except ValidationException, e:
                return (form,None,e.errors)
    return (form,None,[])

def update_and_redirect(form_instance,form_class,request,template_name, redirect_to,success_msg=_('Your request was processed successfully')):
    def save(request,form):
        instance=form.save()
        return locals()
    return edit_and_redirect(form_instance,form_class,request,template_name,redirect_to,save,success_msg)


def update(id, form_class,form_extras,request,template_name, redirect_to,success_msg=_('Your request was processed successfully'),extra_context=None,processor=None,ajax=False):
    def save(request,form):
        instance=form.save()
        return locals()
    form_processor=processor
    if not form_processor: form_processor=save
    model=form_class.Meta.model
    instance=model.objects.filter(id=id)
    if not instance.exists(): raise Http404
    form_init={'instance':instance[0]}
    form_init.update(form_extras)
    form_instance=form_class(**form_init)
    form=form_instance
    results={}
    msg=''
    if request.method=='POST':
        form = form_class(request.POST,request.FILES,instance=instance[0])
        if form.is_valid():
            try:
                results = form_processor(request,form)
                request.flash['message']=success_msg
                if ajax : 
                    json_results=_preprocess_results(results.copy())
                    return success_json(success_msg, json_results)
                return redirect(redirect_to)
            except ValidationException, e:
                msg=e.errors
                request.flash['message']=msg
    results['instance']=instance[0]
    results['form']=form
    if extra_context: results.update(extra_context)
    if ajax : return error_json([msg], {'form':form.errors},_preprocess_results(results.copy()))
    return render_to_response(template_name, results, request)

def _preprocess_results(results):
    #Cannot serialize model forms!
    if 'form' in results: del results['form']
    if 'instance' in results:
        results['instance']= serializers.serialize('json', [results['instance']])
    return results
class ValidationException(Exception):
    def __init__(self,errors=None):
        self.errors=errors

def load_class(path):
    i = path.rfind('.')
    from django.utils.importlib import import_module
    module, attr = path[:i], path[i+1:]
    try:
        mod = import_module(module)
    except ImportError, e:
        raise ImproperlyConfigured('Error importing class %s: "%s"' % (module, e))
    except ValueError, e:
        raise ImproperlyConfigured('Error class')
    try:
        return getattr(mod, attr)
    except AttributeError:
        raise ImproperlyConfigured('Module "%s" does not define class "%s"' % (module, attr))

## {{{ http://code.activestate.com/recipes/576693/ (r6)

class OrderedDict(dict, DictMixin):

    def __init__(self, *args, **kwds):
        if len(args) > 1:
            raise TypeError('expected at most 1 arguments, got %d' % len(args))
        try:
            self.__end
        except AttributeError:
            self.clear()
        self.update(*args, **kwds)

    def clear(self):
        self.__end = end = []
        end += [None, end, end]         # sentinel node for doubly linked list
        self.__map = {}                 # key --> [key, prev, next]
        dict.clear(self)

    def __setitem__(self, key, value):
        if key not in self:
            end = self.__end
            curr = end[1]
            curr[2] = end[1] = self.__map[key] = [key, curr, end]
        dict.__setitem__(self, key, value)

    def __delitem__(self, key):
        dict.__delitem__(self, key)
        key, prev, next = self.__map.pop(key)
        prev[2] = next
        next[1] = prev

    def __iter__(self):
        end = self.__end
        curr = end[2]
        while curr is not end:
            yield curr[0]
            curr = curr[2]

    def __reversed__(self):
        end = self.__end
        curr = end[1]
        while curr is not end:
            yield curr[0]
            curr = curr[1]

    def popitem(self, last=True):
        if not self:
            raise KeyError('dictionary is empty')
        if last:
            key = reversed(self).next()
        else:
            key = iter(self).next()
        value = self.pop(key)
        return key, value

    def __reduce__(self):
        items = [[k, self[k]] for k in self]
        tmp = self.__map, self.__end
        del self.__map, self.__end
        inst_dict = vars(self).copy()
        self.__map, self.__end = tmp
        if inst_dict:
            return (self.__class__, (items,), inst_dict)
        return self.__class__, (items,)

    def keys(self):
        return list(self)

    setdefault = DictMixin.setdefault
    update = DictMixin.update
    pop = DictMixin.pop
    values = DictMixin.values
    items = DictMixin.items
    iterkeys = DictMixin.iterkeys
    itervalues = DictMixin.itervalues
    iteritems = DictMixin.iteritems

    def __repr__(self):
        if not self:
            return '%s()' % (self.__class__.__name__,)
        return '%s(%r)' % (self.__class__.__name__, self.items())

    def copy(self):
        return self.__class__(self)

    @classmethod
    def fromkeys(cls, iterable, value=None):
        d = cls()
        for key in iterable:
            d[key] = value
        return d

    def __eq__(self, other):
        if isinstance(other, OrderedDict):
            return len(self)==len(other) and self.items() == other.items()
        return dict.__eq__(self, other)


    def __ne__(self, other):
        return not self == other
## end of http://code.activestate.com/recipes/576693/ }}}


def absolute_url(request, url):
    current_uri = '%s://%s%s' % (request.is_secure() and 'https' or 'http',
                             request.get_host(),url)
    return iri_to_uri(current_uri)
