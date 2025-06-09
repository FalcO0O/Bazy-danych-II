import React, { useState, useEffect, useContext, createContext } from 'react';
import { User, Gavel, TrendingUp, Clock, Users, BarChart3, LogOut, Menu, X, Plus, Eye, Edit, Shield, Award, DollarSign } from 'lucide-react';

const AuthContext = createContext(null);

class ApiService {
  constructor() {
    this.baseURL = 'http://localhost:8000';
  }

  async request(endpoint, options = {}) {
    const token = localStorage.getItem('access_token');
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...(token && { Authorization: `Bearer ${token}` }),
      },
      ...options,
    };

    const response = await fetch(`${this.baseURL}${endpoint}`, config);
    
    if (response.status === 401) {
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const refreshResponse = await fetch(`${this.baseURL}/token/refresh`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh_token: refreshToken }),
          });
          
          if (refreshResponse.ok) {
            const data = await refreshResponse.json();
            localStorage.setItem('access_token', data.access_token);
            localStorage.setItem('refresh_token', data.refresh_token);
            
            config.headers.Authorization = `Bearer ${data.access_token}`;
            return fetch(`${this.baseURL}${endpoint}`, config);
          }
        } catch (error) {
          this.logout();
        }
      }
      this.logout();
      throw new Error('Authentication required');
    }

    return response;
  }

  async login(email, password) {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);

    const response = await fetch(`${this.baseURL}/login`, {
      method: 'POST',
      body: formData,
    });

    if (response.ok) {
      const data = await response.json();
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('refresh_token', data.refresh_token);
      return data;
    }
    throw new Error('Login failed');
  }

  async register(userData) {
    const response = await fetch(`${this.baseURL}/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(userData),
    });

    if (response.ok) {
      return response.json();
    }
    throw new Error('Registration failed');
  }

  logout() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    window.location.reload();
  }

  async getAuctions() {
    const response = await this.request('/auctions');
    return response.json();
  }

  async createAuction(auctionData) {
    const response = await this.request('/auctions', {
      method: 'POST',
      body: JSON.stringify(auctionData),
    });
    return response.json();
  }

  async placeBid(auctionId, amount) {
    const response = await this.request(`/auctions/${auctionId}/bid`, {
      method: 'POST',
      body: JSON.stringify({ amount }),
    });
    return response.json();
  }

  async closeAuction(auctionId) {
    const response = await this.request(`/auctions/${auctionId}/close`, {
      method: 'POST',
    });
    return response.json();
  }

  async getReports() {
    const response = await this.request('/reports/history');
    return response.json();
  }

  async getUserSpending() {
    const response = await this.request('/reports/user-spending');
    return response.json();
  }

  async getTopWinners() {
    const response = await this.request('/reports/top-winners');
    return response.json();
  }

  async getAuctionStats() {
    const response = await this.request('/reports/auctions-stats');
    return response.json();
  }
}

const api = new ApiService();

function useAuth() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        setUser({ id: payload.sub, role: payload.role });
      } catch (error) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
      }
    }
    setLoading(false);
  }, []);

  const login = async (email, password) => {
    try {
      await api.login(email, password);
      const token = localStorage.getItem('access_token');
      const payload = JSON.parse(atob(token.split('.')[1]));
      setUser({ id: payload.sub, role: payload.role });
      return true;
    } catch (error) {
      throw error;
    }
  };

  const logout = () => {
    api.logout();
    setUser(null);
  };

  return { user, login, logout, loading };
}

function LoginForm({ onSwitchToRegister }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useContext(AuthContext);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await login(email, password);
    } catch (err) {
      log(err)
      setError('Nieprawidłowy email lub hasło');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900 flex items-center justify-center p-4">
      <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 w-full max-w-md border border-white/20">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full mb-4">
            <Gavel className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-white mb-2">AuctionHub</h1>
          <p className="text-gray-300">Zaloguj się do swojego konta</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <input
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            />
          </div>
          <div>
            <input
              type="password"
              placeholder="Hasło"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            />
          </div>

          {error && (
            <div className="text-red-400 text-sm text-center">{error}</div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white font-semibold rounded-lg transition-all duration-200 disabled:opacity-50"
          >
            {loading ? 'Logowanie...' : 'Zaloguj się'}
          </button>
        </form>

        <div className="mt-6 text-center">
          <button
            onClick={onSwitchToRegister}
            className="text-gray-300 hover:text-white transition-colors"
          >
            Nie masz konta? Zarejestruj się
          </button>
        </div>
      </div>
    </div>
  );
}

function RegisterForm({ onSwitchToLogin }) {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    if (formData.password !== formData.confirmPassword) {
      setError('Hasła nie są identyczne');
      setLoading(false);
      return;
    }

    try {
      await api.register({
        username: formData.username,
        email: formData.email,
        password: formData.password
      });
      onSwitchToLogin();
    } catch (err) {
      setError('Błąd podczas rejestracji');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900 flex items-center justify-center p-4">
      <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 w-full max-w-md border border-white/20">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full mb-4">
            <Gavel className="w-8 h-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-white mb-2">AuctionHub</h1>
          <p className="text-gray-300">Utwórz nowe konto</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="text"
            placeholder="Nazwa użytkownika"
            value={formData.username}
            onChange={(e) => setFormData({...formData, username: e.target.value})}
            className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            required
          />
          <input
            type="email"
            placeholder="Email"
            value={formData.email}
            onChange={(e) => setFormData({...formData, email: e.target.value})}
            className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            required
          />
          <input
            type="password"
            placeholder="Hasło"
            value={formData.password}
            onChange={(e) => setFormData({...formData, password: e.target.value})}
            className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            required
          />
          <input
            type="password"
            placeholder="Potwierdź hasło"
            value={formData.confirmPassword}
            onChange={(e) => setFormData({...formData, confirmPassword: e.target.value})}
            className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            required
          />

          {error && (
            <div className="text-red-400 text-sm text-center">{error}</div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white font-semibold rounded-lg transition-all duration-200 disabled:opacity-50"
          >
            {loading ? 'Rejestracja...' : 'Zarejestruj się'}
          </button>
        </form>

        <div className="mt-6 text-center">
          <button
            onClick={onSwitchToLogin}
            className="text-gray-300 hover:text-white transition-colors"
          >
            Masz już konto? Zaloguj się
          </button>
        </div>
      </div>
    </div>
  );
}

function Navigation({ activeTab, setActiveTab, user, logout }) {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const navItems = [
    { id: 'auctions', label: 'Aukcje', icon: Gavel },
    { id: 'create', label: 'Utwórz aukcję', icon: Plus },
    ...(user?.role === 'admin' ? [
      { id: 'reports', label: 'Raporty', icon: BarChart3 },
      { id: 'users', label: 'Użytkownicy', icon: Users }
    ] : [])
  ];

  return (
    <nav className="bg-white/10 backdrop-blur-lg border-b border-white/20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center">
            <div className="flex items-center space-x-2">
              <Gavel className="w-8 h-8 text-blue-400" />
              <span className="text-xl font-bold text-white">AuctionHub</span>
            </div>
          </div>

          <div className="hidden md:flex items-center space-x-8">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`flex items-center space-x-2 px-3 py-2 rounded-lg transition-colors ${
                    activeTab === item.id
                      ? 'bg-blue-500 text-white'
                      : 'text-gray-300 hover:text-white hover:bg-white/10'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{item.label}</span>
                </button>
              );
            })}
            <button
              onClick={logout}
              className="flex items-center space-x-2 px-3 py-2 rounded-lg text-gray-300 hover:text-white hover:bg-white/10 transition-colors"
            >
              <LogOut className="w-4 h-4" />
              <span>Wyloguj</span>
            </button>
          </div>

          <div className="md:hidden">
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="text-gray-300 hover:text-white"
            >
              {isMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>

        {isMenuOpen && (
          <div className="md:hidden py-4 space-y-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <button
                  key={item.id}
                  onClick={() => {
                    setActiveTab(item.id);
                    setIsMenuOpen(false);
                  }}
                  className={`w-full flex items-center space-x-2 px-3 py-2 rounded-lg transition-colors ${
                    activeTab === item.id
                      ? 'bg-blue-500 text-white'
                      : 'text-gray-300 hover:text-white hover:bg-white/10'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{item.label}</span>
                </button>
              );
            })}
            <button
              onClick={logout}
              className="w-full flex items-center space-x-2 px-3 py-2 rounded-lg text-gray-300 hover:text-white hover:bg-white/10 transition-colors"
            >
              <LogOut className="w-4 h-4" />
              <span>Wyloguj</span>
            </button>
          </div>
        )}
      </div>
    </nav>
  );
}

function AuctionCard({ auction, onBid, onClose, user }) {
  const [bidAmount, setBidAmount] = useState('');
  const [showBidForm, setShowBidForm] = useState(false);

  const handleBid = async (e) => {
    e.preventDefault();
    if (bidAmount && parseFloat(bidAmount) > auction.current_price) {
      await onBid(auction.id, parseFloat(bidAmount));
      setBidAmount('');
      setShowBidForm(false);
    }
  };

  const canClose = user?.role === 'admin' || user?.id === auction.owner_id;

  return (
    <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20 hover:border-white/30 transition-all duration-200">
      <div className="flex justify-between items-start mb-4">
        <h3 className="text-xl font-semibold text-white">{auction.title}</h3>
        {canClose && (
          <button
            onClick={() => onClose(auction.id)}
            className="px-3 py-1 bg-red-500 hover:bg-red-600 text-white text-sm rounded-lg transition-colors"
          >
            Zamknij
          </button>
        )}
      </div>
      
      {auction.description && (
        <p className="text-gray-300 mb-4">{auction.description}</p>
      )}
      
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <DollarSign className="w-5 h-5 text-green-400" />
          <span className="text-2xl font-bold text-green-400">
            {auction.current_price.toFixed(2)} zł
          </span>
        </div>
        <div className="flex items-center space-x-2 text-gray-400 text-sm">
          <Clock className="w-4 h-4" />
          <span>{new Date(auction.created_at).toLocaleDateString('pl-PL')}</span>
        </div>
      </div>

      <div className="space-y-3">
        {!showBidForm ? (
          <button
            onClick={() => setShowBidForm(true)}
            className="w-full py-3 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white font-semibold rounded-lg transition-all duration-200"
          >
            Licytuj
          </button>
        ) : (
          <form onSubmit={handleBid} className="space-y-3">
            <input
              type="number"
              step="0.01"
              min={auction.current_price + 0.01}
              placeholder={`Min. ${(auction.current_price + 0.01).toFixed(2)} zł`}
              value={bidAmount}
              onChange={(e) => setBidAmount(e.target.value)}
              className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            />
            <div className="flex space-x-2">
              <button
                type="submit"
                className="flex-1 py-2 bg-green-500 hover:bg-green-600 text-white font-semibold rounded-lg transition-colors"
              >
                Potwierdź
              </button>
              <button
                type="button"
                onClick={() => setShowBidForm(false)}
                className="flex-1 py-2 bg-gray-500 hover:bg-gray-600 text-white font-semibold rounded-lg transition-colors"
              >
                Anuluj
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}

function AuctionsList() {
  const [auctions, setAuctions] = useState([]);
  const [loading, setLoading] = useState(true);
  const { user } = useContext(AuthContext);

  const loadAuctions = async () => {
    try {
      const data = await api.getAuctions();
      setAuctions(data);
    } catch (error) {
      console.error('Error loading auctions:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAuctions();
  }, []);

  const handleBid = async (auctionId, amount) => {
    try {
      await api.placeBid(auctionId, amount);
      await loadAuctions();
    } catch (error) {
      alert('Błąd podczas licytacji');
    }
  };

  const handleClose = async (auctionId) => {
    try {
      await api.closeAuction(auctionId);
      await loadAuctions();
    } catch (error) {
      alert('Błąd podczas zamykania aukcji');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-white">Aktywne aukcje</h2>
        <div className="text-gray-300">
          {auctions.length} {auctions.length === 1 ? 'aukcja' : 'aukcji'}
        </div>
      </div>

      {auctions.length === 0 ? (
        <div className="text-center py-12">
          <Gavel className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-400 text-lg">Brak aktywnych aukcji</p>
        </div>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {auctions.map((auction) => (
            <AuctionCard
              key={auction.id}
              auction={auction}
              onBid={handleBid}
              onClose={handleClose}
              user={user}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function CreateAuction() {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    starting_price: ''
  });
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      await api.createAuction({
        title: formData.title,
        description: formData.description,
        starting_price: parseFloat(formData.starting_price)
      });
      setSuccess(true);
      setFormData({ title: '', description: '', starting_price: '' });
      setTimeout(() => setSuccess(false), 3000);
    } catch (error) {
      alert('Błąd podczas tworzenia aukcji');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-white/10 backdrop-blur-lg rounded-xl p-8 border border-white/20">
        <h2 className="text-2xl font-bold text-white mb-6">Utwórz nową aukcję</h2>

        {success && (
          <div className="mb-6 p-4 bg-green-500/20 border border-green-500/30 rounded-lg text-green-300">
            Aukcja została utworzona pomyślnie!
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-gray-300 mb-2">Tytuł aukcji</label>
            <input
              type="text"
              value={formData.title}
              onChange={(e) => setFormData({...formData, title: e.target.value})}
              className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            />
          </div>

          <div>
            <label className="block text-gray-300 mb-2">Opis</label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({...formData, description: e.target.value})}
              rows={4}
              className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-gray-300 mb-2">Cena startowa (zł)</label>
            <input
              type="number"
              step="0.01"
              min="0.01"
              value={formData.starting_price}
              onChange={(e) => setFormData({...formData, starting_price: e.target.value})}
              className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white font-semibold rounded-lg transition-all duration-200 disabled:opacity-50"
          >
            {loading ? 'Tworzenie...' : 'Utwórz aukcję'}
          </button>
        </form>
      </div>
    </div>
  );
}

function Reports() {
  const [stats, setStats] = useState(null);
  const [topWinners, setTopWinners] = useState([]);
  const [userSpending, setUserSpending] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadReports = async () => {
      try {
        const [statsData, winnersData, spendingData] = await Promise.all([
          api.getAuctionStats(),
          api.getTopWinners(),
          api.getUserSpending()
        ]);
        setStats(statsData);
        setTopWinners(winnersData);
        setUserSpending(spendingData);
      } catch (error) {
        console.error('Error loading reports:', error);
      } finally {
        setLoading(false);
      }
    };

    loadReports();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <h2 className="text-2xl font-bold text-white">Raporty i statystyki</h2>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-300 text-sm">Aktywne aukcje</p>
              <p className="text-2xl font-bold text-white">{stats?.auctions_active || 0}</p>
            </div>
            <TrendingUp className="w-8 h-8 text-blue-400" />
          </div>
        </div>

        <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-300 text-sm">Zamknięte aukcje</p>
              <p className="text-2xl font-bold text-white">{stats?.auctions_closed || 0}</p>
            </div>
            <Gavel className="w-8 h-8 text-green-400" />
          </div>
        </div>

        <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-300 text-sm">Łączna wartość</p>
              <p className="text-2xl font-bold text-white">{stats?.total_value?.toFixed(2) || '0.00'} zł</p>
            </div>
            <DollarSign className="w-8 h-8 text-yellow-400" />
          </div>
        </div>

        <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-300 text-sm">Użytkownicy</p>
              <p className="text-2xl font-bold text-white">{stats?.total_users || 0}</p>
            </div>
            <Users className="w-8 h-8 text-purple-400" />
          </div>
        </div>
      </div>

      <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
        <h3 className="text-xl font-semibold text-white mb-4 flex items-center">
          <Award className="w-5 h-5 mr-2 text-yellow-400" />
          Najlepsi licytanci
        </h3>
        <div className="space-y-3">
          {topWinners.map((winner, index) => (
            <div key={winner.id} className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
              <div className="flex items-center space-x-3">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
                  index === 0 ? 'bg-yellow-500 text-yellow-900' :
                  index === 1 ? 'bg-gray-400 text-gray-900' :
                  index === 2 ? 'bg-amber-600 text-amber-100' :
                  'bg-gray-600 text-gray-300'
                }`}>
                  {index + 1}
                </div>
                <div>
                  <p className="text-white font-medium">{winner.username}</p>
                  <p className="text-gray-400 text-sm">{winner.won_auctions} wygranych aukcji</p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-white font-semibold">{winner.total_spent?.toFixed(2)} zł</p>
                <p className="text-gray-400 text-sm">wydane</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
        <h3 className="text-xl font-semibold text-white mb-4 flex items-center">
          <BarChart3 className="w-5 h-5 mr-2 text-blue-400" />
          Wydatki użytkowników
        </h3>
        <div className="space-y-3">
          {userSpending.map((user) => (
            <div key={user.id} className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
              <div>
                <p className="text-white font-medium">{user.username}</p>
                <p className="text-gray-400 text-sm">{user.bids_count} licytacji</p>
              </div>
              <div className="text-right">
                <p className="text-white font-semibold">{user.total_spent?.toFixed(2)} zł</p>
                <div className="w-24 bg-gray-700 rounded-full h-2 mt-1">
                  <div 
                    className="bg-blue-500 h-2 rounded-full" 
                    style={{width: `${Math.min((user.total_spent / Math.max(...userSpending.map(u => u.total_spent))) * 100, 100)}%`}}
                  ></div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function UserManagement() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    const loadUsers = async () => {
      try {
        const response = await api.request('/users');
        const data = await response.json();
        setUsers(data);
      } catch (error) {
        console.error('Error loading users:', error);
      } finally {
        setLoading(false);
      }
    };

    loadUsers();
  }, []);

  const handleToggleUserStatus = async (userId, currentStatus) => {
    try {
      await api.request(`/users/${userId}/toggle-status`, {
        method: 'POST'
      });
      setUsers(users.map(user => 
        user.id === userId 
          ? { ...user, is_active: !currentStatus }
          : user
      ));
    } catch (error) {
      alert('Błąd podczas zmiany statusu użytkownika');
    }
  };

  const handlePromoteUser = async (userId) => {
    try {
      await api.request(`/users/${userId}/promote`, {
        method: 'POST'
      });
      setUsers(users.map(user => 
        user.id === userId 
          ? { ...user, role: 'admin' }
          : user
      ));
    } catch (error) {
      alert('Błąd podczas promowania użytkownika');
    }
  };

  const filteredUsers = users.filter(user =>
    user.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
    user.email.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-white">Zarządzanie użytkownikami</h2>
        <div className="text-gray-300">
          {users.length} {users.length === 1 ? 'użytkownik' : 'użytkowników'}
        </div>
      </div>

      <div className="bg-white/10 backdrop-blur-lg rounded-xl p-4 border border-white/20">
        <input
          type="text"
          placeholder="Szukaj użytkowników..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>

      <div className="bg-white/10 backdrop-blur-lg rounded-xl border border-white/20 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-white/5">
              <tr>
                <th className="px-6 py-4 text-left text-gray-300 font-medium">Użytkownik</th>
                <th className="px-6 py-4 text-left text-gray-300 font-medium">Email</th>
                <th className="px-6 py-4 text-left text-gray-300 font-medium">Rola</th>
                <th className="px-6 py-4 text-left text-gray-300 font-medium">Status</th>
                <th className="px-6 py-4 text-left text-gray-300 font-medium">Data rejestracji</th>
                <th className="px-6 py-4 text-left text-gray-300 font-medium">Akcje</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/10">
              {filteredUsers.map((user) => (
                <tr key={user.id} className="hover:bg-white/5">
                  <td className="px-6 py-4">
                    <div className="flex items-center">
                      <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                        <User className="w-5 h-5 text-white" />
                      </div>
                      <div className="ml-3">
                        <p className="text-white font-medium">{user.username}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-gray-300">{user.email}</td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
                      user.role === 'admin' 
                        ? 'bg-purple-500/20 text-purple-300 border border-purple-500/30'
                        : 'bg-gray-500/20 text-gray-300 border border-gray-500/30'
                    }`}>
                      {user.role === 'admin' ? 'Administrator' : 'Użytkownik'}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
                      user.is_active 
                        ? 'bg-green-500/20 text-green-300 border border-green-500/30'
                        : 'bg-red-500/20 text-red-300 border border-red-500/30'
                    }`}>
                      {user.is_active ? 'Aktywny' : 'Nieaktywny'}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-gray-300 text-sm">
                    {new Date(user.created_at).toLocaleDateString('pl-PL')}
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex space-x-2">
                      <button
                        onClick={() => handleToggleUserStatus(user.id, user.is_active)}
                        className={`px-3 py-1 text-xs font-medium rounded transition-colors ${
                          user.is_active
                            ? 'bg-red-500/20 text-red-300 hover:bg-red-500/30 border border-red-500/30'
                            : 'bg-green-500/20 text-green-300 hover:bg-green-500/30 border border-green-500/30'
                        }`}
                      >
                        {user.is_active ? 'Dezaktywuj' : 'Aktywuj'}
                      </button>
                      {user.role !== 'admin' && (
                        <button
                          onClick={() => handlePromoteUser(user.id)}
                          className="px-3 py-1 text-xs font-medium rounded bg-purple-500/20 text-purple-300 hover:bg-purple-500/30 border border-purple-500/30 transition-colors"
                        >
                          Promuj
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {filteredUsers.length === 0 && (
        <div className="text-center py-12">
          <Users className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-400 text-lg">Nie znaleziono użytkowników</p>
        </div>
      )}
    </div>
  );
}

function AuctionApp() {
  const auth = useAuth();
  const [activeTab, setActiveTab] = useState('auctions');
  const [showLogin, setShowLogin] = useState(true);

  if (auth.loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (!auth.user) {
    return (
      <AuthContext.Provider value={auth}>
        {showLogin ? (
          <LoginForm onSwitchToRegister={() => setShowLogin(false)} />
        ) : (
          <RegisterForm onSwitchToLogin={() => setShowLogin(true)} />
        )}
      </AuthContext.Provider>
    );
  }

  const renderContent = () => {
    switch (activeTab) {
      case 'auctions':
        return <AuctionsList />;
      case 'create':
        return <CreateAuction />;
      case 'reports':
        return auth.user.role === 'admin' ? <Reports /> : <AuctionsList />;
      case 'users':
        return auth.user.role === 'admin' ? <UserManagement /> : <AuctionsList />;
      default:
        return <AuctionsList />;
    }
  };

  return (
    <AuthContext.Provider value={auth}>
      <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900">
        <Navigation
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          user={auth.user}
          logout={auth.logout}
        />
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {renderContent()}
        </main>
      </div>
    </AuthContext.Provider>
  );
}

export default AuctionApp;