function getAnchorsPos() {
	let pages = document.getElementById('content').querySelectorAll('.page');
	let pages_pos = {}
	pages.forEach((el) => {
		pages_pos[el.id] = el.offsetTop;
	});

	return pages_pos;
}

function getMenuLinks() {
	let menu = document.getElementById('nav-menu');
	let menu_links = menu.querySelectorAll('.menu-list a');
	let links = {}
	menu_links.forEach((el) => {
		links[el.hash.replace('#', '')] = el;
	});

	return links;
}

function highlightMenu() {
	let scroll_pos = document.documentElement.scrollTop || document.body.scrollTop;

	for (let i in anchors) {
		if (anchors[i] >= scroll_pos - 100) {
			for (let i in menu_links) {
				menu_links[i].classList.remove('active');
			}
			menu_links[i].classList.add('active');
			break;
		}
	}
}

function toggleMenu() {
	let menu = document.getElementById('nav-menu');
	menu.classList.toggle('show');
}

function closeMenu() {
	let menu = document.getElementById('nav-menu');
	menu.classList.remove('show');	
}


/// RUN 
let anchors;
let menu_links;

// do the menu highlighting
window.addEventListener('DOMContentLoaded', ()=> {
	anchors = getAnchorsPos();
	menu_links = getMenuLinks()

	highlightMenu();

	// listen to the menu button (mobile only)
	document.getElementById('toggle-menu-button').addEventListener('click', (ev) => {
		toggleMenu();
	});

	document.getElementById('content').addEventListener('click', (ev) => {
		closeMenu();
	});

	window.addEventListener('scroll', (ev) => {
		highlightMenu();
	});
});


