import React, { useEffect, useState } from "react";
import { useAppDispatch, useAppSelector } from "../hooks";
import { userRegister } from "../features/auth/authActions";
import { useNavigate } from "react-router-dom";

const Register: React.FC = () => {
  const dispatch = useAppDispatch();
  const { loading, error, success } = useAppSelector((state) => state.auth);
  const [firstName, setFirstName] = useState<string>("");
  const [lastName, setLastName] = useState<string>("");
  const [email, setEmail] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const [gln, setGln] = useState<string>("");
  const [phoneNumber, setPhoneNumber] = useState<string>("");
  const [address, setAddress] = useState<string>("");

  const navigate = useNavigate();

  useEffect(() => {
    if (success) {
      navigate("/login");
    }
  }, [navigate, success]);

  const handleRegister = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const form = e.currentTarget;
    if (form.checkValidity() === false) {
      e.stopPropagation();
    } else {
      const registerData = {
        firstName,
        lastName,
        email,
        password,
        gln,
        phoneNumber,
        address,
      };
      dispatch(userRegister(registerData));
    }
    form.classList.add("was-validated");
  };

  return (
    <div>
      <div>
        <form onSubmit={handleRegister}>
          {error && (
            <div className="alert alert-danger" role="alert">
              {error}
            </div>
          )}
          <div className="mb-3">
            <label htmlFor="first-name" className="form-label">
              İsim
            </label>
            <input
              type="text"
              className="form-control"
              id="first-name"
              value={firstName}
              onChange={(e) => setFirstName(e.target.value)}
              required
              onInvalid={(e) =>
                (e.target as HTMLInputElement).setCustomValidity(
                  "Lütfen isminizi giriniz."
                )
              }
              onInput={(e) =>
                (e.target as HTMLInputElement).setCustomValidity("")
              }
            />
          </div>
          <div className="mb-3">
            <label htmlFor="last-name" className="form-label">
              Soyisim
            </label>
            <input
              type="text"
              className="form-control"
              id="last-name"
              value={lastName}
              onChange={(e) => setLastName(e.target.value)}
              required
              onInvalid={(e) =>
                (e.target as HTMLInputElement).setCustomValidity(
                  "Lütfen soyisminizi giriniz."
                )
              }
              onInput={(e) =>
                (e.target as HTMLInputElement).setCustomValidity("")
              }
            />
          </div>
          <div className="mb-3">
            <label htmlFor="email" className="form-label">
              Email
            </label>
            <input
              type="email"
              className="form-control"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              autoComplete="email"
              required
              onInvalid={(e) =>
                (e.target as HTMLInputElement).setCustomValidity(
                  "Lütfen email adresinizi giriniz."
                )
              }
              onInput={(e) =>
                (e.target as HTMLInputElement).setCustomValidity("")
              }
            />
          </div>
          <div className="mb-3">
            <label htmlFor="password" className="form-label">
              Şifre
            </label>
            <input
              type="password"
              className="form-control"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="current-password"
              required
              onInvalid={(e) =>
                (e.target as HTMLInputElement).setCustomValidity(
                  "Lütfen şifre giriniz."
                )
              }
              onInput={(e) =>
                (e.target as HTMLInputElement).setCustomValidity("")
              }
            />
          </div>
          <div className="mb-3">
            <label htmlFor="gln" className="form-label">
              GLN
            </label>
            <input
              type="number"
              className="form-control"
              id="gln"
              value={gln}
              min="1000000000000"
              max="9999999999999"
              onChange={(e) => setGln(e.target.value)}
              onInvalid={(e) =>
                (e.target as HTMLInputElement).setCustomValidity(
                  "Lütfen 13 haneli GLN numaranızı giriniz."
                )
              }
              onInput={(e) =>
                (e.target as HTMLInputElement).setCustomValidity("")
              }
            />
          </div>
          <div className="mb-3">
            <label htmlFor="phone-number" className="form-label">
              Phone Number
            </label>
            <input
              type="text"
              className="form-control"
              id="phone-number"
              value={phoneNumber}
              onChange={(e) => setPhoneNumber(e.target.value)}
            />
          </div>
          <div className="mb-3">
            <label htmlFor="address" className="form-label">
              Adres
            </label>
            <input
              type="text"
              className="form-control"
              id="address"
              value={address}
              onChange={(e) => setAddress(e.target.value)}
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary w-100"
            disabled={loading}
          >
            Kayıt ol
          </button>
        </form>
      </div>
      <div className="text-center mt-3"></div>
    </div>
  );
};

export default Register;
