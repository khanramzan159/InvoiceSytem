import re
from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponse
from .models import User,Admin,Invoice,Item
from hashlib import sha256
from django.contrib import messages
from django.db.models import Q
from .forms import InvoiceForm, ItemFormSet
from django.core.mail import send_mail
from django.conf import settings
import random

from io import BytesIO
from django.template.loader import get_template
from django.views import View
from xhtml2pdf import pisa


# Sending email 
def generation_otp():
    otp = ""
    for i in range(6):
        otp += str(random.randint(0, 9))
    return otp
def send_email_to_client(email, subject, keyword):
    subject = subject
    otp_code = generation_otp()
    message = f'Your OTP code {keyword} is :{otp_code}'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, from_email, recipient_list)
    return otp_code

def home(request):
    if request.session.has_key('admin'):
        return redirect(admin)
    if request.session.has_key('login'):  
        user = request.session['user']
        user_det = User.objects.get(name=user)
        invoices = Invoice.objects.filter(created_by=user_det)
        context = {
            'user': user,
            'email': user_det.email,
            'id': user_det.id,   
            'status': user_det.status,
            'invoices': invoices
        }   
        return render(request, 'loginreg/home.html', context)
    else:   
        if request.session.has_key('logerror'):
            messages.error(request, 'Invalid credentials!')
            del request.session['logerror'] 
        elif request.session.has_key('blockerror'):  
            messages.error(request, 'user blocked!')
            del request.session['blockerror'] 
        return render(request, 'loginreg/index.html')

def changepassword(request):
    if request.session.has_key('admin'):
        return redirect(admin)
    if request.session.has_key('login'):
        if request.session.has_key('update'):
            messages.success(request, 'Password updated!')
            del request.session['update']
        if request.session.has_key('error'):
            messages.error(request, 'Invalid password!')
            del request.session['error']    
        user = request.session['user']
        user_det = User.objects.get(name=user)
        context = {
            'user': user,
            'email': user_det.email,
            'id': user_det.id,   
            'status': user_det.status
        }   
        return render(request, 'loginreg/change_pass.html', context)
    else:   
        return render(request, 'loginreg/index.html')

def login(request):
    if request.session.has_key('login'):
        return redirect(home)
    else:    
        if request.POST:
            uname = request.POST['uname']
            passw = request.POST['pass']
            passwenc = sha256(passw.encode()).hexdigest()
            user = User.objects.filter(name=uname,password=passwenc)
            if user:
                user = User.objects.get(name=uname)
                request.session['login'] = 1
                request.session['user'] = uname
                return redirect(home)
                # if user.status == 1:
                #     request.session['login'] = 1
                #     request.session['user'] = uname
                #     return redirect(home)
                # else:
                #     request.session['blockerror'] = 1   
                #     return redirect(home)   
            else:
                request.session['logerror'] = 1
                return redirect(home)
        else:
            return redirect(home)

def logout(request):
    request.session.flush()
    return redirect(home)

def signup(request):
    if request.session.has_key('admin'):
        return redirect(admin)
    if request.session.has_key('login'):
        return redirect(home)
    else:    
        if request.POST:
            uname = request.POST.get('uname', '')
            email = request.POST.get('email', '')
            passw = request.POST.get('pass', '')
            passwenc = sha256(passw.encode()).hexdigest()
            user = User.objects.filter(name=uname)
            if user:
                messages.error(request, 'username already exists!')
                return render(request, 'loginreg/signup.html')
            else:  
                user = User.objects.filter(email=email)
                if user:
                    messages.error(request, 'email already exists!')
                    return render(request, 'loginreg/signup.html')
                else:
                    try:
                        otp_code = send_email_to_client(email, "Email Verification for Registeration from Aryansh Electricals", "for Registration")
                        request.session['otp_code'] = otp_code 
                        request.session['signup_data'] = {
                            'uname_u': uname,
                            'email': email,
                            'password':passwenc
                        }    
                        print(uname)
                        messages.success(request, 'OTP has been sent on your registered Email')
                        return redirect('verify_otp')
                    except Exception as e:
                        messages.error(request, str("Network Issue try again"))
                        return render(request, 'loginreg/signup.html')
        else:
            return render(request, 'loginreg/signup.html')

def changep(request):
    if request.session.has_key('admin'):
        return redirect(admin)
    if request.POST:
        cpass = request.POST['curpass']
        oldpasswenc = sha256(cpass.encode()).hexdigest()
        npass = request.POST['npass']
        uname = request.session['user']
        user = User.objects.filter(name=uname)
        for i in user:
            if i.password == oldpasswenc:
                passwenc = sha256(npass.encode()).hexdigest()
                User.objects.filter(name=uname).update(password=passwenc)
                request.session['update'] = 1
                return redirect(changepassword)
            else:
                request.session['error'] = 1
                return redirect(changepassword)               
    else:
        return redirect(changepassword)    

def admin(request):
    if request.session.has_key('user'):
        return redirect(home)
    if request.session.has_key('admin'):  
        if request.session.has_key('deleterr'):
            messages.error(request, 'no such user to delete!') 
            del request.session['deleterr']
        if request.session.has_key('deletesucc'):
            messages.success(request, 'User deleted successfully!')   
            del request.session['deletesucc']    
        if request.session.has_key('updateuser'):
            messages.success(request, 'User updated successfully!')   
            del request.session['updateuser']
        if request.session.has_key('createuser'):
            messages.success(request, 'User added successfully!')   
            del request.session['createuser']   
        if request.session.has_key('searchuser'):
            messages.error(request, 'No such user!')   
            del request.session['searchuser']   
        users = User.objects.all()            
        return render(request, 'loginreg/admin.html', {'dets': users})
    elif request.POST:
        usern = request.POST.get('username')
        passw = request.POST.get('password')
        # passwenc = sha256(passw.encode()).hexdigest()
        admins = Admin.objects.filter(username=usern,password=passw)
        if admins:
            request.session['admin'] = 1
            return redirect(admin)
        else:    
            return render(request, 'loginreg/admin-login.html', {'error': 'Invalid credentials!'})      
    else:    
        return render(request, 'loginreg/admin-login.html')   

def admin_invoices(request):
    if request.session.has_key('user'):
        return redirect(home)
    if request.session.has_key('admin'):  
        all_invoices = Invoice.objects.all()            
        return render(request, 'loginreg/admin_invoices.html', {'invoices': all_invoices})
    else:
        return redirect(admin)  

def admin_create_invoice(request):
    if request.session.has_key('admin'):
        if request.method == 'POST':
            invoice_form = InvoiceForm(request.POST)
            item_formset = ItemFormSet(request.POST, prefix='items')

            if invoice_form.is_valid() and item_formset.is_valid():
                # Save the invoice form to get the invoice instance
                invoice = invoice_form.save(commit=False)
                # invoice.created_by = 'Admin'
                
                invoice.save()
                # Save the item forms with the reference to the invoice
                items = item_formset.save(commit=False)
                for item in items:
                    item.invoice = invoice
                    item.save()

                invoice.save()
                messages.success(request , "New Invoice has been created")
                return redirect(admin_invoices)
            else:
                # Handle form validation errors
                return render(request, 'loginreg/create_invoice.html', {'invoice_form': invoice_form, 'item_formset': item_formset, 'error':"An error Occured"})
        else:
            invoice_form = InvoiceForm()
            item_formset = ItemFormSet(prefix='items')
            return render(request, 'loginreg/create_invoice.html', {'invoice_form': invoice_form, 'item_formset': item_formset})
    else:
        return redirect(admin_invoices)   
    
def admin_update_invoice(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    if request.method == 'POST':
        invoice_form = InvoiceForm(request.POST, instance=invoice)
        item_formset = ItemFormSet(request.POST, instance=invoice, prefix='items')

        if invoice_form.is_valid() and item_formset.is_valid():
            invoice_form.save()
            item_formset.save()
            invoice_form.save()

            messages.success(request , (f"Invoice No. {invoice_id} has been Updated!"))
            return redirect(admin_invoices)
        else:
            # Handle form validation errors
            return render(request, 'loginreg/update_invoice.html', {'invoice_form': invoice_form, 'item_formset': item_formset, 'invoice_id': invoice_id})
    else:
        invoice_form = InvoiceForm(instance=invoice)
        item_formset = ItemFormSet(instance=invoice, prefix='items')
        return render(request, 'loginreg/update_invoice.html', {'invoice_form': invoice_form, 'item_formset': item_formset, 'invoice_id': invoice_id})

def admin_delete_invoice(request , invoice_id):
    invoice = Invoice.objects.get(id=invoice_id)
    invoice.delete()
    messages.success(request , (f"Invoice No. {invoice_id} has been deleted!"))
    return redirect(admin_invoices)

def view(request):
    if request.session.has_key('user'):
        return redirect(home)
    if request.session.has_key('admin'):
        if request.session.has_key('blocked'):
            messages.success(request, 'User blocked!')
            del request.session['blocked']
        if request.session.has_key('unblocked'):
            messages.success(request, 'User unblocked!')
            del request.session['unblocked']
        if request.session.has_key('blockid'):
            id = request.session['blockid']
            del request.session['blockid']
        else:    
            id = request.GET.get('id')
        user = User.objects.filter(id=id)
        if user:
            if request.session.has_key('updateerroru'):
                messages.error(request, 'Username already exists!')
                del request.session['updateerroru']
            elif request.session.has_key('updateerrore'):
                messages.error(request, 'Email already exists!')
                del request.session['updateerrore']     
            userdet = User.objects.get(id=id)
            return render(request, 'loginreg/view.html', {'user': userdet})  
        else:
            return render(request, 'loginreg/view.html', {'error': 'No such user!'})     
    else:
        return redirect(admin)
    
def delete(request):
    if request.session.has_key('user'):
        return redirect(home)
    if request.session.has_key('admin'):
        id = request.GET.get('id', '')
        user = User.objects.filter(id=id)
        if user:
            User.objects.filter(id=id).delete()
            request.session['deletesucc'] = 1
            return redirect(admin)
        else:
            request.session['deleterr'] = 1
            return redirect(admin)   
    else:
        return redirect(admin)

def save(request):
    if request.session.has_key('user'):
        return redirect(home)
    if request.session.has_key('admin'):    
        if request.POST:
            id = request.POST.get('id')
            usern = request.POST.get('usern')
            email = request.POST.get('email')  
            user = User.objects.filter(id=id)
            if user:
                userval = User.objects.filter(Q(name=usern), ~Q(id=id))
                if userval:
                    request.session['updateerroru'] = 1
                    request.session['blockid'] = id
                    return redirect(view)
                else:
                    if User.objects.filter(Q(email=email), ~Q(id=id)):
                        request.session['updateerrore'] = 1
                        request.session['blockid'] = id
                        return redirect(view)  
                    else:     
                        User.objects.filter(id=id).update(name=usern,email=email)
                        request.session['updateuser'] = 1
                        return redirect(admin)
            else:
                return redirect(admin)      
        else:
            return redirect(admin)              
    else:
        return redirect(admin)

def block(request):
    if request.session.has_key('user'):
        return redirect(home)
    if request.session.has_key('admin'):
        id = request.GET.get('id', '')
        user = User.objects.filter(id=id)
        if user:
            userd = User.objects.get(id=id)
            if userd.status == 1:
                user = User.objects.filter(id=id).update(status=0)
                request.session['blocked'] = 1
                request.session['block'] = 1
            elif userd.status == 0:
                user = User.objects.filter(id=id).update(status=1)  
                request.session['unblocked'] = 1  
                request.session['block'] = 0  
            request.session['blockid'] = id    
            return redirect(view)  
    else:
        return redirect(admin)  

def search(request):
    if request.session.has_key('user'):
        return redirect(home)
    if request.session.has_key('admin'): 
        if request.POST:
            usern = request.POST['username']
            user = User.objects.filter(name=usern)
            if user:
                user = User.objects.get(name=usern)
                id = user.id
                request.session['blockid'] = id    
                return redirect(view) 
            else:
                request.session['searchuser'] = 1
                return redirect(admin)
    else:
        return redirect(admin)
    



def adminlogout(request):
    if request.session.has_key('user'):
        return redirect(home)
    if request.session.has_key('admin'): 
        request.session.flush()
        return redirect(admin)
    else:
        return redirect(admin)

def create(request):
    if request.session.has_key('user'):
        return redirect(home)
    if request.session.has_key('admin'): 
        if request.POST:
            usern = request.POST.get('username')
            email = request.POST.get('email')
            passw = request.POST.get('pass')
            passwenc = sha256(passw.encode()).hexdigest()
            user = User.objects.filter(name=usern)
            if user:
                return render(request, 'loginreg/create.html', {'error': 'username already exists!'})
            else:
                user = User.objects.filter(email=email)
                if user:
                    return render(request, 'loginreg/create.html', {'error': 'email already exists!'})
                else:
                    obj = User()
                    obj.name = usern
                    obj.password = passwenc
                    obj.email = email
                    obj.save()
                    request.session['createuser'] = 1
                    return redirect(admin)
        else:    
            return render(request, 'loginreg/create.html')
    else:
        return redirect(admin)


def create_invoice(request):
    if request.session.has_key('login'):
        if User.objects.get(name=request.session['user']).status == 0:
            messages.warning(request, ('You are not an active user'))
            return redirect(home)
    return create_invoice2(request)
# creating invoice
def create_invoice2(request):
    if request.session.has_key('login'):
        user_instance = User.objects.get(name=request.session['user'])
        if request.method == 'POST':
            invoice_form = InvoiceForm(request.POST)
            item_formset = ItemFormSet(request.POST, prefix='items')

            if invoice_form.is_valid() and item_formset.is_valid():
                # Save the invoice form to get the invoice instance
                invoice = invoice_form.save(commit=False)
                invoice.created_by = user_instance
                
                invoice.save()
                # Save the item forms with the reference to the invoice
                items = item_formset.save(commit=False)
                for item in items:
                    item.invoice = invoice
                    item.save()

                invoice.save()
                messages.success(request , "New Invoice has been created")
                return redirect(home)
            else:
                # Handle form validation errors
                return render(request, 'loginreg/create_invoice.html', {'invoice_form': invoice_form, 'item_formset': item_formset, 'error':"An error Occured"})
        else:
            invoice_form = InvoiceForm()
            item_formset = ItemFormSet(prefix='items')
            return render(request, 'loginreg/create_invoice.html', {'invoice_form': invoice_form, 'item_formset': item_formset})
    else:
        return redirect(home)
    

def update_invoice(request, invoice_id):
    if request.session.has_key('admin'):
        return redirect(admin)
    if request.session.has_key('login'):
        user_instance = User.objects.get(name=request.session['user'])
        invoice = get_object_or_404(Invoice, id=invoice_id)
        if user_instance.status == 0 or invoice.created_by != user_instance:
            messages.warning(request, ('You Are Not Allowed to do this'))
            return redirect(home)
        return update_invoice2(request, invoice_id)
    return redirect(home)

def update_invoice2(request, invoice_id):
            
    invoice = get_object_or_404(Invoice, id=invoice_id)
    if request.method == 'POST':
        invoice_form = InvoiceForm(request.POST, instance=invoice)
        item_formset = ItemFormSet(request.POST, instance=invoice, prefix='items')

        if invoice_form.is_valid() and item_formset.is_valid():
            invoice_form.save()
            item_formset.save()
            invoice_form.save()
            messages.success(request , (f"Invoice No. {invoice_id} has been Updated!"))
            return redirect(home)
        else:
            # Handle form validation errors
            return render(request, 'loginreg/update_invoice.html', {'invoice_form': invoice_form, 'item_formset': item_formset, 'invoice_id': invoice_id})
    else:
        invoice_form = InvoiceForm(instance=invoice)
        item_formset = ItemFormSet(instance=invoice, prefix='items')
        return render(request, 'loginreg/update_invoice.html', {'invoice_form': invoice_form, 'item_formset': item_formset, 'invoice_id': invoice_id})

def delete_invoice(request , invoice_id):
    user_instance = User.objects.get(name=request.session['user'])
    invoice = Invoice.objects.get(id=invoice_id)
    if user_instance.status == 1 and invoice.created_by == user_instance:        
        invoice.delete()
        messages.success(request , (f"Invoice No. {invoice_id} has been deleted!"))
        return redirect(home)
    else:
        messages.warning(request, ('You Are Not Allowed to do this'))
        return redirect(home)
    
def show_invoice_history(request , invoice_id):
    if request.session.has_key('user'):
        return redirect(home)
    if request.session.has_key('admin'):  
        invoice = get_object_or_404(Invoice, pk=invoice_id)
        history = invoice.history.all()
        return render(request, 'loginreg/show_invoice_history.html', {'invoice': invoice, 'history': history})
    else:
        return redirect(admin)



# OTP
def verify_otp(request):
    signup_data = request.session.get('signup_data', {})
    uname = signup_data.get('uname_u')
    email = signup_data.get('email')
    password = signup_data.get('password')
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        user_email = request.POST.get('email')
        if 'otp_code' in request.session:
            otp_code = request.session['otp_code']

            if entered_otp == otp_code:
                print("Till here ------")

                obj = User()
                obj.name = uname
                obj.email = email
                obj.password = password
                obj.status = False
                obj.save()

                print("Done-----------")
                request.session['login'] = 1
                request.session['user'] = uname

                del request.session['otp_code']  # Remove the OTP code from the session
                del request.session['signup_data']

                return redirect(home)
            # OTP is incorrect, display an error message
        messages.error(request, 'Invalid OTP. Please try again.')
        return render(request, 'loginreg/otp_verification.html', {'user_email': user_email})
    else:
        return render(request, 'loginreg/otp_verification.html', {'user_email': email})




# PDF

def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None


def pdf_view(request, invoice_id):
    if request.session.has_key('admin'):
        return pdf_view2(request, invoice_id)
    elif request.session.has_key('login'):
        user_instance = User.objects.get(name=request.session['user'])
        invoice = get_object_or_404(Invoice, id=invoice_id)
        if user_instance.status != 0 and invoice.created_by == user_instance:
            return pdf_view2(request, invoice_id)
        else:
            return HttpResponse("404 PAGE NOT FOUND", status=404)
    else:
        return HttpResponse("404 PAGE NOT FOUND", status=404)

def pdf_view2(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    items = Item.objects.filter(invoice=invoice)
    data = {
        'invoice': invoice,
        'items': items
    }
    pdf = render_to_pdf('loginreg/pdf_template.html', data)
    
    if pdf:
        return pdf
    else:
        return HttpResponse("Error generating PDF", status=500)

def email_verification(request):
    if request.session.has_key('admin'):
        return redirect(admin)
    if request.session.has_key('login'):
        return redirect(home)
    else:    
        if request.POST:
            email = request.POST.get('forgot_password_email', '')
            user = User.objects.filter(email=email)
            if not user:
                messages.error(request, 'Email does not exist, Please Register')
                return render(request, 'loginreg/email_verification.html')
            else:
                try:
                    otp_code = send_email_to_client(email, "Forgot Password", "for Resetting the Password")
                    request.session['otp_code'] = otp_code 
                    request.session['forgot_password_data'] = {
                        'email': email
                    }
                    messages.success(request, 'OTP has been sent on your registered Email')
                    return redirect('reset_password')
                except Exception as e:
                    messages.error(request, str("Network Issue try again"))
                    return render(request, 'loginreg/email_verification.html')
        else:
            return render(request, 'loginreg/email_verification.html')


def reset_password(request):
    forgot_password_data = request.session.get('forgot_password_data', {})
    email = forgot_password_data.get('email')
    # uname = request.session.get('user')
    if request.session.has_key('admin'):
        return redirect(admin)
    if request.session.has_key('login'):
        return redirect(home)
    else:
        if request.POST:
            entered_otp = request.POST.get('otp')
            if 'otp_code' in request.session:
                otp_code = request.session['otp_code']
                if entered_otp == otp_code:
                    passw = request.POST.get('pass', '')
                    passwenc = sha256(passw.encode()).hexdigest()
                    print("Till here ------")
                    user = User.objects.get(email=email)
                    uname = user.name
                    user.password = passwenc
                    user.status = False
                    user.save()
                    print("Done-----------")
                    # request.session['user'] = uname
                    del request.session['otp_code']  # Remove the OTP code from the session
                    del request.session['forgot_password_data']
                    messages.success(request, 'Password is being Reset ')
                    return redirect(login)
                else:
                    messages.error(request, 'Invalid OTP. Please try again.')
                    return render(request, 'loginreg/reset_password.html', {'user_email': email})
            else:
                messages.error(request, 'Please Request the OTP.')
                return render(request, 'loginreg/reset_password.html', {'user_email': email})
        else:
            return render(request, 'loginreg/reset_password.html', {'user_email': email})