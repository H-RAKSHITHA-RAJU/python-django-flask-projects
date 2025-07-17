from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import requests
from .models import WordSearchHistory
from .forms import SignUpForm


def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Signup successful!")
            return redirect('home')
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


def Signin_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, "Sign in successful!")
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, 'signin.html')


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "Logged out successfully.")
    return redirect('signin')


def home(request):
    return render(request, 'home.html')


def get_antonyms_wordsapi(word):
    url = f"https://wordsapiv1.p.rapidapi.com/words/{word}/antonyms"
    headers = {
        "X-RapidAPI-Key": "YOUR_RAPIDAPI_KEY",  # Replace this with your actual RapidAPI key
        "X-RapidAPI-Host": "wordsapiv1.p.rapidapi.com"
    }
    try:
        response = requests.get(url, headers=headers, timeout=5)
        data = response.json()
        return data.get("antonyms", [])
    except Exception as e:
        print("WordsAPI antonym fetch failed:", e)
        return []


@login_required
def word(request):
    search = request.GET.get('search', '').strip()
    if not search:
        context = {
            "meaning": "",
            "synonyms": [],
            "antonyms": [],
            "pronunciation": "",
            "search": "",
        }
        return render(request, 'word.html', context)

    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{search}"

    meaning = "No definition found."
    pronunciation = "Pronunciation not found"
    synonyms = []
    antonyms = []

    try:
        response = requests.get(url, timeout=5)
        data = response.json()

        if isinstance(data, list) and data:
            # Get Meaning
            if data[0].get("meanings"):
                meaning = data[0]["meanings"][0]["definitions"][0]["definition"]

            # Get Pronunciation
            phonetics = data[0].get("phonetics", [])
            for p in phonetics:
                if p.get("text"):
                    pronunciation = p["text"]
                    break

            # Get Synonyms & Antonyms
            for meaning_entry in data[0].get("meanings", []):
                for defn in meaning_entry.get("definitions", []):
                    synonyms += defn.get("synonyms", [])
                    antonyms += defn.get("antonyms", [])

            synonyms = list(set(synonyms))
            antonyms = list(set(antonyms))

    except Exception as e:
        print("Error from Dictionary API:", e)

    # Fallback: Datamuse API
    if not synonyms:
        try:
            syn_response = requests.get(f"https://api.datamuse.com/words?rel_syn={search}", timeout=5)
            syn_data = syn_response.json()
            synonyms = [item["word"] for item in syn_data]
        except Exception as e:
            print("Datamuse synonym fallback failed:", e)

    if not antonyms:
        try:
            ant_response = requests.get(f"https://api.datamuse.com/words?rel_ant={search}", timeout=5)
            ant_data = ant_response.json()
            antonyms = [item["word"] for item in ant_data]
        except Exception as e:
            print("Datamuse antonym fallback failed:", e)

    # Final fallback to WordsAPI
    if not antonyms:
        antonyms = get_antonyms_wordsapi(search)

    # ✅ Save search history
    WordSearchHistory.objects.create(
        user=request.user,
        word=search,
        meaning=meaning,
        synonyms=synonyms,
        antonyms=antonyms,
        pronunciation=pronunciation
    )

    context = {
        "meaning": meaning,
        "synonyms": synonyms or ["No synonyms found."],
        "antonyms": antonyms or ["No antonyms found."],
        "pronunciation": pronunciation,
        "search": search,
    }

    return render(request, 'word.html', context)



@login_required
def history_view(request):
    histories = WordSearchHistory.objects.filter(user=request.user).order_by('-searched_at')
    return render(request, 'history.html', {'histories': histories})
