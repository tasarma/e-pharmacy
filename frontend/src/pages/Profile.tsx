import { useAppSelector } from "../hooks";

const Profile = () => {
    const {userInfo }= useAppSelector((state) => state.auth.userInfo);

  return (
    <div>
      <figure>{userInfo?.firstName.charAt(0).toUpperCase()}</figure>
      <span>
        Welcome <strong>{userInfo?.firstName}!</strong> You can view this page
        because you're logged in
      </span>
    </div>
  )
}
export default Profile