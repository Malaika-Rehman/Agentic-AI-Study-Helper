import re
import streamlit as st
import streamlit.components.v1 as components
from data.database import register_user, set_onboarding_completed
from components.about_section import render_signup_about


# Password Strength HTML+JS — runs client-side only, password never leaves the browser
_PW_HTML = '<style>\n.pw-wrap{margin-top:6px;padding:12px 14px;background:#FDF7F8;border:1px solid #EADCE0;border-radius:10px;font-family:Arial,sans-serif;font-size:12.5px;color:#4A3A40;}\n.pw-top{display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;}\n.pw-lbl{font-weight:700;font-size:11px;letter-spacing:.04em;text-transform:uppercase;}\n.pw-track{height:5px;background:#EADCE0;border-radius:100px;overflow:hidden;margin-bottom:10px;}\n.pw-fill{height:5px;border-radius:100px;transition:width .35s,background .35s;}\n.pw-list{display:flex;flex-direction:column;gap:4px;}\n.pw-item{display:flex;align-items:center;gap:7px;font-size:11.5px;color:#9E828D;transition:color .2s;}\n.pw-item.ok{color:#16A34A;}\n.pw-ico{width:14px;text-align:center;font-size:12px;}\n</style>\n<div class="pw-wrap">\n  <div class="pw-top">\n    <span class="pw-lbl">Password Strength</span>\n    <span class="pw-lbl" id="pws-lbl" style="color:#9E828D">&#8212;</span>\n  </div>\n  <div class="pw-track"><div class="pw-fill" id="pws-bar" style="width:0%;background:#EADCE0;"></div></div>\n  <div class="pw-list">\n    <div class="pw-item" id="c-len"><span class="pw-ico">&#9675;</span><span>At least 8 characters</span></div>\n    <div class="pw-item" id="c-up"><span class="pw-ico">&#9675;</span><span>Uppercase letter (A&#8211;Z)</span></div>\n    <div class="pw-item" id="c-lo"><span class="pw-ico">&#9675;</span><span>Lowercase letter (a&#8211;z)</span></div>\n    <div class="pw-item" id="c-num"><span class="pw-ico">&#9675;</span><span>Number (0&#8211;9)</span></div>\n    <div class="pw-item" id="c-sp"><span class="pw-ico">&#9675;</span><span>Special character (!@#$%&hellip;)</span></div>\n  </div>\n</div>\n<script>\n(function(){\n  var W=["password","password1","password123","12345678","123456789",\n    "1234567890","qwerty","qwerty123","qwertyuiop","abc123","iloveyou",\n    "letmein","welcome","monkey","dragon","master","sunshine","princess",\n    "football","shadow","superman","login","admin","root","pass","test",\n    "passw0rd","p@ssword","p@ssw0rd","hello","hello123","baseball",\n    "starwars","trustno1","changeme"];\n  var S=["01234","12345","23456","34567","45678","56789","12345678",\n    "abcdef","bcdefg","cdefgh","qwerty","asdfgh","zxcvbn","qwertyuiop","asdfghjkl"];\n  function hasSeq(p){var l=p.toLowerCase();for(var i=0;i<S.length;i++){if(l.indexOf(S[i])!==-1)return true;}return false;}\n  function hasRep(p){return/(.)\\1{3,}/.test(p);}\n  function score(p){\n    if(!p)return 0;\n    var lo=p.toLowerCase();\n    for(var i=0;i<W.length;i++){if(lo===W[i])return 1;}\n    if(hasSeq(p))return 2;\n    var s=0;\n    if(hasRep(p))s=Math.max(s-1,0);\n    if(p.length>=8)s++;\n    if(p.length>=12)s++;\n    if(/[A-Z]/.test(p))s++;\n    if(/[a-z]/.test(p))s++;\n    if(/[0-9]/.test(p))s++;\n    if(/[^A-Za-z0-9]/.test(p))s++;\n    return Math.min(s,5);\n  }\n  var LV=[\n    {t:"Very Weak",  c:"#DC2626",w:"16%"},\n    {t:"Very Weak",  c:"#DC2626",w:"16%"},\n    {t:"Weak",       c:"#EA580C",w:"32%"},\n    {t:"Medium",     c:"#D97706",w:"55%"},\n    {t:"Strong",     c:"#16A34A",w:"80%"},\n    {t:"Very Strong",c:"#15803D",w:"100%"}\n  ];\n  function render(p){\n    var bar=document.getElementById("pws-bar"),lbl=document.getElementById("pws-lbl");\n    if(!bar||!lbl)return;\n    if(!p){bar.style.width="0%";bar.style.background="#EADCE0";lbl.innerHTML="&#8212;";lbl.style.color="#9E828D";}\n    else{var lv=LV[score(p)]||LV[0];bar.style.width=lv.w;bar.style.background=lv.c;lbl.textContent=lv.t;lbl.style.color=lv.c;}\n    tick("c-len",p.length>=8);\n    tick("c-up",/[A-Z]/.test(p));\n    tick("c-lo",/[a-z]/.test(p));\n    tick("c-num",/[0-9]/.test(p));\n    tick("c-sp",/[^A-Za-z0-9]/.test(p));\n  }\n  function tick(id,ok){\n    var el=document.getElementById(id);if(!el)return;\n    var ic=el.querySelector(".pw-ico");\n    el.className=ok?"pw-item ok":"pw-item";\n    ic.innerHTML=ok?"&#10003;":"&#9675;";\n  }\n  function findPw(){\n    var doc=window.parent.document;\n    var all=doc.querySelectorAll("input[type=\'password\']");\n    for(var i=0;i<all.length;i++){\n      var w=all[i].closest("[data-testid=\'stTextInput\']");\n      if(w){var lb=w.querySelector("label");if(lb&&lb.textContent.trim()==="Password")return all[i];}\n    }\n    return all[0]||null;\n  }\n  var _last=null;\n  function poll(){var inp=findPw();if(inp&&inp.value!==_last){_last=inp.value;render(_last);}setTimeout(poll,130);}\n  setTimeout(poll,900);\n})();\n</script>\n'


def render_signup():
    col_left, col_right = st.columns([1.15, 1], gap="large")

    with col_left:
        st.markdown(
            '<div class="app-topbar">'
            '<span class="logo">🎓</span>'
            '<span class="name">Agentic AI Study Helper</span>'
            '</div>',
            unsafe_allow_html=True,
        )
        render_signup_about()

    with col_right:
        st.markdown("<div class='section-title' style='margin-bottom:4px'>Create Account</div>",
                    unsafe_allow_html=True)
        st.markdown("<div class='muted' style='margin-bottom:20px'>Fill in your details below</div>",
                    unsafe_allow_html=True)

        with st.form("signup_form"):
            name = st.text_input("Full Name", placeholder="Enter your full name")

            # Roll Number is OPTIONAL — users may leave it blank
            student_id = st.text_input(
                "Roll Number (Optional)",
                placeholder="e.g. 2024-CS-001 (optional)",
            )

            email = st.text_input("Email Address", placeholder="Enter your email address")

            password = st.text_input(
                "Password", type="password", placeholder="Create a strong password"
            )

            confirm = st.text_input(
                "Confirm Password", type="password", placeholder="Re-enter your password"
            )

            submitted = st.form_submit_button(
                "Create Account →",
                use_container_width=True,
                type="primary",
            )

        # Dynamic password strength indicator (outside the form)
        components.html(_PW_HTML, height=185, scrolling=False)

        if submitted:
            # Roll Number is OPTIONAL — excluded from required-field check
            if not all([name, email, password, confirm]):
                st.error(
                    "Please fill in all required fields "
                    "(Full Name, Email, Password, Confirm Password)."
                )

            elif len(password) < 8:
                st.error("Password must be at least 8 characters long.")

            elif not re.search(r"[A-Z]", password):
                st.error("Password must contain at least one uppercase letter (A-Z).")

            elif not re.search(r"[a-z]", password):
                st.error("Password must contain at least one lowercase letter (a-z).")

            elif not re.search(r"\d", password):
                st.error("Password must contain at least one number (0-9).")

            elif not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=/\\\[\]\';`~]', password):
                st.error(
                    "Password must contain at least one special character "
                    "such as ! @ # $ % & *"
                )

            elif password != confirm:
                st.error("Passwords do not match.")

            else:
                success, message = register_user(
                    email, password, name,
                    student_id,  # may be empty string
                )
                if success:
                    set_onboarding_completed()
                    st.success("🎉 Account created! Please sign in.")
                    st.session_state.just_registered = True
                    import time
                    time.sleep(1)
                    st.session_state.screen = "login"
                    st.rerun()
                else:
                    st.error(f"❌ {message}")

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

        if st.button("Already have an account? Sign in →", use_container_width=True):
            st.session_state.screen = "login"
            st.rerun()

        if st.button("← Back to Welcome", use_container_width=True):
            st.session_state.screen = "onboarding"
            st.rerun()
