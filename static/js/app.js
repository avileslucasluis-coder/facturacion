const apiBase = '/api';

const selectors = {
    loginScreen: document.getElementById('loginScreen'),
    dashboardScreen: document.getElementById('dashboardScreen'),
    loginForm: document.getElementById('loginForm'),
    logoutBtn: document.getElementById('logoutBtn'),
    loginMessage: document.getElementById('loginMessage'),
    pageTitle: document.getElementById('pageTitle'),
    pageSubtitle: document.getElementById('pageSubtitle'),
    userName: document.getElementById('userName'),
    notifications: document.getElementById('notifications'),
    errors: document.getElementById('errors'),
    searchInput: document.getElementById('searchInput'),
    newActionBtn: document.getElementById('newActionBtn'),
    productsTable: document.querySelector('#productsTable tbody'),
    invoicesTable: document.querySelector('#invoicesTable tbody'),
    providersTable: document.querySelector('#providersTable tbody'),
    countProducts: document.getElementById('countProducts'),
    countInvoices: document.getElementById('countInvoices'),
    countProviders: document.getElementById('countProviders'),
    aiStatus: document.getElementById('aiStatus'),
    reportSalesTotal: document.getElementById('reportSalesTotal'),
    reportInvoiceCount: document.getElementById('reportInvoiceCount'),
    reportInventoryCount: document.getElementById('reportInventoryCount'),
    aiInsights: document.getElementById('aiInsights'),
};

const sections = Array.from(document.querySelectorAll('.dashboard-section'));
const navButtons = Array.from(document.querySelectorAll('.sidebar-nav .nav-item'));

let currentSection = 'overviewSection';

const auth = {
    getToken() {
        return localStorage.getItem('access_token');
    },
    setToken(value) {
        localStorage.setItem('access_token', value);
    },
    clear() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('current_user');
    }
};

function showNotification(message) {
    selectors.notifications.textContent = message;
    selectors.notifications.classList.remove('hidden');
    setTimeout(() => selectors.notifications.classList.add('hidden'), 5000);
}

function showError(message) {
    selectors.errors.textContent = message;
    selectors.errors.classList.remove('hidden');
    setTimeout(() => selectors.errors.classList.add('hidden'), 7000);
}

function updateHeader(label) {
    selectors.pageTitle.textContent = label || 'Bienvenido';
    selectors.pageSubtitle.textContent = label === 'Inicio'
        ? 'Visualiza el estado general de tu ERP.'
        : 'Gestiona tu operación administrativa.';
}

async function showSection(id) {
    sections.forEach(section => {
        section.classList.toggle('active', section.id === id);
    });
    navButtons.forEach(btn => btn.classList.toggle('active', btn.dataset.target === id));
    const activeLabel = navButtons.find(btn => btn.dataset.target === id);
    updateHeader(activeLabel ? activeLabel.textContent : 'Inicio');
    currentSection = id;
}

async function fetchWithAuth(path, options = {}) {
    const token = auth.getToken();
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers,
    };
    if (token) {
        headers.Authorization = `Bearer ${token}`;
    }
    const res = await fetch(`${apiBase}${path}`, {
        ...options,
        headers,
    });
    if (res.status === 401) {
        auth.clear();
        renderAuthState();
        throw new Error('Sesión expirada. Inicia sesión de nuevo.');
    }
    const data = await res.json();
    if (!res.ok) {
        const error = data.detail || data.message || data.error || 'Error desconocido';
        throw new Error(error);
    }
    return data;
}

async function handleLogin(event) {
    event.preventDefault();
    selectors.loginMessage.textContent = '';
    const username = document.getElementById('loginUsername').value.trim();
    const password = document.getElementById('loginPassword').value.trim();

    if (!username || !password) {
        selectors.loginMessage.textContent = 'Usuario y contraseña son obligatorios.';
        return;
    }

    try {
        const data = await fetch(`${apiBase}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password }),
        });
        const result = await data.json();
        if (!data.ok) {
            throw new Error(result.detail || result.error || 'Error en login');
        }
        auth.setToken(result.access_token);
        selectors.loginMessage.classList.remove('danger');
        selectors.loginMessage.classList.add('success');
        selectors.loginMessage.textContent = 'Login exitoso. Cargando panel...';
        await initializeDashboard();
    } catch (error) {
        selectors.loginMessage.classList.remove('success');
        selectors.loginMessage.classList.add('danger');
        selectors.loginMessage.textContent = error.message;
    }
}

function renderAuthState() {
    const token = auth.getToken();
    if (token) {
        selectors.loginScreen.classList.add('hidden');
        selectors.dashboardScreen.classList.add('active');
        selectors.dashboardScreen.classList.remove('hidden');
        selectors.loginMessage.classList.add('hidden');
    } else {
        selectors.loginScreen.classList.remove('hidden');
        selectors.dashboardScreen.classList.remove('active');
        selectors.dashboardScreen.classList.add('hidden');
        selectors.loginMessage.classList.add('hidden');
    }
}

async function loadProfile() {
    try {
        const data = await fetchWithAuth('/auth/me');
        const name = data.username || 'Usuario';
        selectors.userName.textContent = name;
    } catch (error) {
        showError(error.message);
    }
}

async function loadProducts() {
    try {
        const data = await fetchWithAuth('/products');
        const products = data.products || [];
        selectors.productsTable.innerHTML = products.map(product => `
            <tr>
                <td>${product.id}</td>
                <td>${product.name}</td>
                <td>$${product.price.toFixed(2)}</td>
                <td>${(product.tax_rate * 100).toFixed(0)}%</td>
            </tr>
        `).join('');
        selectors.countProducts.textContent = products.length;
    } catch (error) {
        showError(error.message);
    }
}

async function loadInvoices() {
    try {
        const data = await fetchWithAuth('/invoices');
        const invoices = data.invoices || [];
        selectors.invoicesTable.innerHTML = invoices.map(invoice => `
            <tr>
                <td>${invoice.id}</td>
                <td>${invoice.invoice_number}</td>
                <td>${invoice.date.split('T')[0] || invoice.date}</td>
                <td>$${invoice.total?.toFixed(2) || '0.00'}</td>
                <td>${invoice.status}</td>
            </tr>
        `).join('');
        selectors.countInvoices.textContent = invoices.length;
    } catch (error) {
        showError(error.message);
    }
}

async function loadProviders() {
    try {
        const data = await fetchWithAuth('/providers');
        const providers = data.providers || [];
        selectors.providersTable.innerHTML = providers.map(provider => `
            <tr>
                <td>${provider.id}</td>
                <td>${provider.name}</td>
                <td>${provider.ruc || '-'}</td>
                <td>${provider.phone || '-'}</td>
            </tr>
        `).join('');
        selectors.countProviders.textContent = providers.length;
    } catch (error) {
        showError(error.message);
    }
}

async function loadAiStatus() {
    try {
        const data = await fetchWithAuth('/ai/status');
        selectors.aiStatus.textContent = data.available ? 'Disponible' : 'Offline';
    } catch (error) {
        selectors.aiStatus.textContent = 'No disponible';
    }
}

async function createProduct(event) {
    event.preventDefault();
    const payload = {
        name: document.getElementById('productName').value.trim(),
        price: parseFloat(document.getElementById('productPrice').value),
        tax_rate: parseFloat(document.getElementById('productTax').value),
    };
    try {
        await fetchWithAuth('/products', {
            method: 'POST',
            body: JSON.stringify(payload),
        });
        showNotification('Producto guardado correctamente');
        document.getElementById('productForm').reset();
        await loadProducts();
    } catch (error) {
        showError(error.message);
    }
}

async function createInvoice(event) {
    event.preventDefault();
    const payload = {
        invoice_number: document.getElementById('invoiceNumber').value.trim(),
    };
    try {
        await fetchWithAuth('/invoices', {
            method: 'POST',
            body: JSON.stringify(payload),
        });
        showNotification('Factura creada correctamente');
        document.getElementById('invoiceForm').reset();
        await loadInvoices();
    } catch (error) {
        showError(error.message);
    }
}

async function addInvoiceItem(event) {
    event.preventDefault();
    const invoiceId = parseInt(document.getElementById('invoiceItemInvoiceId').value, 10);
    const payload = {
        product_id: parseInt(document.getElementById('invoiceItemProductId').value, 10) || null,
        description: document.getElementById('invoiceItemDescription').value.trim(),
        quantity: parseInt(document.getElementById('invoiceItemQuantity').value, 10),
        unit_price: parseFloat(document.getElementById('invoiceItemUnitPrice').value),
        tax_rate: parseFloat(document.getElementById('invoiceItemTax').value),
    };
    try {
        await fetchWithAuth(`/invoices/${invoiceId}/items`, {
            method: 'POST',
            body: JSON.stringify(payload),
        });
        showNotification('Item añadido a la factura');
        document.getElementById('invoiceItemForm').reset();
    } catch (error) {
        showError(error.message);
    }
}

async function createProvider(event) {
    event.preventDefault();
    const payload = {
        name: document.getElementById('providerName').value.trim(),
        ruc: document.getElementById('providerRuc').value.trim(),
        email: document.getElementById('providerEmail').value.trim(),
        phone: document.getElementById('providerPhone').value.trim(),
        address: document.getElementById('providerAddress').value.trim(),
    };
    try {
        await fetchWithAuth('/providers', {
            method: 'POST',
            body: JSON.stringify(payload),
        });
        showNotification('Proveedor registrado correctamente');
        document.getElementById('providerForm').reset();
        await loadProviders();
    } catch (error) {
        showError(error.message);
    }
}

async function loadOverview() {
    await Promise.all([loadProducts(), loadInvoices(), loadProviders(), loadAiStatus()]);
    selectors.reportSalesTotal.textContent = 'Actualiza con IA';
    selectors.reportInvoiceCount.textContent = selectors.countInvoices.textContent;
    selectors.reportInventoryCount.textContent = selectors.countProducts.textContent;
}

async function loadAiInsights() {
    try {
        selectors.aiInsights.textContent = 'Generando insights...';
        const data = await fetchWithAuth('/ai/sales-insights', {
            method: 'POST',
            body: JSON.stringify({
                start_date: new Date(new Date().setDate(new Date().getDate() - 30)).toISOString().slice(0, 10),
                end_date: new Date().toISOString().slice(0, 10),
            }),
        });
        selectors.aiInsights.textContent = JSON.stringify(data.insights, null, 2);
    } catch (error) {
        showError(error.message);
        selectors.aiInsights.textContent = '';
    }
}

async function initializeDashboard() {
    try {
        await loadProfile();
        await loadOverview();
        showSection('overviewSection');
        renderAuthState();
    } catch (error) {
        showError(error.message);
    }
}

function bindEvents() {
    selectors.loginForm.addEventListener('submit', handleLogin);
    selectors.logoutBtn.addEventListener('click', () => {
        auth.clear();
        renderAuthState();
    });
    selectors.newActionBtn.addEventListener('click', () => showSection('invoicesSection'));
    selectors.searchInput && selectors.searchInput.addEventListener('keydown', event => {
        if (event.key === 'Enter') {
            event.preventDefault();
            showSection('reportsSection');
        }
    });

    document.getElementById('productForm').addEventListener('submit', createProduct);
    document.getElementById('invoiceForm').addEventListener('submit', createInvoice);
    document.getElementById('invoiceItemForm').addEventListener('submit', addInvoiceItem);
    document.getElementById('providerForm').addEventListener('submit', createProvider);
    document.getElementById('loadOverviewBtn').addEventListener('click', loadOverview);
    document.getElementById('loadAiInsights').addEventListener('click', loadAiInsights);

    navButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            showSection(btn.dataset.target);
        });
    });
}

window.addEventListener('DOMContentLoaded', async () => {
    bindEvents();
    renderAuthState();
    if (auth.getToken()) {
        await initializeDashboard();
    }
});
