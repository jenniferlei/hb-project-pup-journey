"use strict";

const PetProfile = (props) => {
  // Check if user wants to delete or not
  const deleteConfirm = () => {
    const validate = confirm("Do you want to delete this pet profile?");
    if (validate) {
      deleteExistingPetProfile();
    }
  };

  // Process deletion
  const deleteExistingPetProfile = () => {
    fetch(`/delete-pet/${props.pet_id}`, {
      method: "DELETE",
    }).then((response) => {
      response.json().then((jsonResponse) => {
        // console.log(jsonResponse);
        props.getPetProfiles();
      });
    });
  };

  return (
    <React.Fragment>
      <div className="card ms-4 mb-2" style={{ maxWidth: "540px" }}>
        <div className="row g-0">
          <div className="col-md-4">
            {props.pet_img_URL !== null ? (
              <div>
                <img
                  src={props.pet_img_URL}
                  alt="profile"
                  className="pet-profile-img"
                  id={`pet-img-${props.pet_id}`}
                />
              </div>
            ) : null}
          </div>
          <div className="col-md-8">
            <div className="card-body">
              <div className="clearfix">
                <h5 className="card-title float-start">{props.pet_name}</h5>
                <div className="float-end">
                  <a
                    href=""
                    className="btn btn-sm btn-outline-dark edit-btn"
                    data-bs-toggle="modal"
                    data-bs-target={`#modal-edit-${props.pet_id}`}
                  >
                    <small>
                      <i
                        data-bs-toggle="tooltip"
                        data-bs-placement="right"
                        title="edit pet profile"
                        className="bi bi-pencil"
                      ></i>
                    </small>
                  </a>
                  &nbsp;
                  <button
                    className="btn btn-sm btn-outline-dark delete-btn"
                    type="submit"
                    onClick={deleteConfirm}
                  >
                    <i
                      data-bs-toggle="tooltip"
                      data-bs-placement="right"
                      title="delete pet profile"
                      className="bi bi-x"
                    ></i>
                  </button>
                </div>
              </div>
              <div className="card-tex fw-300">
                {props.breed !== null &&
                props.breed !== "" &&
                props.breed != "None" ? (
                  <div>
                    <small>{props.breed}</small>
                  </div>
                ) : null}

                {props.gender !== null && props.gender !== "" ? (
                  <div>
                    <small>{props.gender}</small>
                  </div>
                ) : null}

                {props.birthday !== null && props.birthday !== "" ? (
                  <div>
                    🎂&nbsp;&nbsp;<small>{props.birthday}</small>
                  </div>
                ) : null}

                {props.check_ins.length !== 0 ? (
                  <React.Fragment>
                    <div>
                      <small>
                        I've done {props.check_ins.length}{" "}
                        {props.check_ins.length === 1 ? (
                          <span>hike</span>
                        ) : (
                          <span>hikes</span>
                        )}
                      </small>
                    </div>
                    <div>
                      <small>
                        and walked&nbsp;
                        {props.total_miles === 1 ? (
                          <span>{props.total_miles} mile</span>
                        ) : (
                          <span>{props.total_miles} miles</span>
                        )}
                        !
                      </small>
                    </div>
                  </React.Fragment>
                ) : null}
              </div>
            </div>
          </div>
        </div>
      </div>
    </React.Fragment>
  );
};

const EditPetProfile = (props) => {
  // Process edit

  const [petName, setPetName] = React.useState(`${props.pet_name}`);
  const [gender, setGender] = React.useState(props.gender);
  const [birthday, setBirthday] = React.useState(
    moment(props.birthday).format("YYYY-MM-DD")
  );
  const [breed, setBreed] = React.useState(props.breed);
  const [imageFile, setImageFile] = React.useState("");

  const editExistingPetProfile = () => {
    const formData = new FormData();

    formData.append("petName", petName);
    formData.append("gender", gender);
    formData.append("birthday", birthday);
    formData.append("breed", breed);

    if (imageFile !== null && typeof imageFile !== "undefined") {
      formData.append("imageFile", imageFile);
    }

    for (const key of formData.entries()) {
      console.log(key);
    }

    fetch(`/edit-pet/${props.pet_id}`, {
      method: "POST",
      body: formData,
    })
      .then((response) => {
        response.json();
      })
      .then((jsonResponse) => {
        props.getPetProfiles();
        // Need to add refresh to AddCheckIns petOptions
        console.log(jsonResponse);
      });
  };
  return (
    <React.Fragment>
      <div
        className="modal fade"
        id={`modal-edit-${props.pet_id}`}
        tabIndex="-1"
        aria-labelledby="modal-edit-pet-label"
        aria-hidden="true"
      >
        <div className="modal-dialog">
          <div className="modal-content">
            <div className="modal-header">
              <h5 className="modal-title" id="modal-edit-pet-label">
                Edit Pet Info
              </h5>
              <button
                type="button"
                className="btn-close"
                data-bs-dismiss="modal"
                aria-label="Close"
              ></button>
            </div>
            <div className="modal-body fw-300">
              <div className="mb-3">
                <label htmlFor="pet_name"> Name </label>&nbsp;
                <small className="text-muted">*</small>
                <input
                  type="text"
                  value={petName}
                  onChange={(event) => setPetName(event.target.value)}
                  className="form-control"
                  placeholder="Name"
                />
              </div>

              <div className="mb-3">
                <label htmlFor="gender"> Gender </label>
                <select
                  selected={gender}
                  onChange={(event) => setGender(event.target.value)}
                  className="form-control"
                >
                  <option value={gender}>{gender}</option>
                  <option value="female">female</option>
                  <option value="male">male</option>
                </select>
              </div>

              <div className="mb-3">
                <label htmlFor="birthday"> Birthday </label>
                <input
                  type="date"
                  value={birthday}
                  onChange={(event) => setBirthday(event.target.value)}
                  className="form-control"
                />
              </div>

              <div className="mb-3">
                <label htmlFor="breed">Breed</label>
                <input
                  type="text"
                  value={breed}
                  onChange={(event) => setBreed(event.target.value)}
                  className="form-control fw-300"
                  placeholder="Breed"
                />
              </div>

              <div className="mb-3">
                <label htmlFor="my_file">Image</label>
                <input
                  type="file"
                  onChange={(event) => setImageFile(event.target.files[0])}
                  className="form-control fw-300"
                  accept="image/png, image/jpeg"
                />
              </div>
              <div className="modal-footer">
                <button
                  type="submit"
                  className="btn btn-sm btn-outline-dark btn-block mt-4 fw-300"
                  data-bs-dismiss="modal"
                  onClick={editExistingPetProfile}
                >
                  Save
                </button>
                <button
                  type="button"
                  className="btn btn-sm btn-secondary btn-block mt-4 fw-300"
                  data-bs-dismiss="modal"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </React.Fragment>
  );
};

const AddPetProfile = (props) => {
  const session_login = document.querySelector("#login").innerText;

  const [petName, setPetName] = React.useState("");
  const [gender, setGender] = React.useState("");
  const [birthday, setBirthday] = React.useState("");
  const [breed, setBreed] = React.useState("");
  const [imageFile, setImageFile] = React.useState("");

  const validatePetProfile = () => {
    const alertText = "Please complete the following:\n• input pet name";

    if (petName === "") {
      alert(alertText);
    } else {
      addNewPetProfile();
    }
  };

  const addNewPetProfile = () => {
    const formData = new FormData();

    formData.append("petName", petName);
    formData.append("gender", gender);
    formData.append("birthday", birthday);
    formData.append("breed", breed);
    formData.append("imageFile", imageFile);

    for (const key of formData.entries()) {
      console.log(key);
    }

    // console.log("petName:", petName);
    // console.log("gender:", gender);
    // console.log("birthday:", birthday);
    // console.log("breed:", breed);
    // console.log("imageFile:", imageFile);

    fetch("/add-pet", {
      method: "POST",
      body: formData,
    }).then((response) => {
      response.json().then((jsonResponse) => {
        props.getPetProfiles();
        console.log(jsonResponse);
      });
    });
  };

  // console.log();

  return (
    <React.Fragment>
      <div
        className="modal fade"
        id="modal-add-pet"
        tabIndex="-1"
        aria-labelledby="modal-add-pet-label"
        aria-hidden="true"
      >
        <div className="modal-dialog">
          <div className="modal-content">
            <div className="modal-header">
              <h5 className="modal-title" id="modal-add-pet-label">
                Add Pet Info
              </h5>
              <button
                type="button"
                className="btn-close"
                data-bs-dismiss="modal"
                aria-label="Close"
              ></button>
            </div>
            <div className="modal-body">
              <div className="mb-3">
                <label htmlFor="pet_name"> Name </label>&nbsp;
                <small className="text-muted">*</small>
                <input
                  type="text"
                  value={petName}
                  onChange={(event) => setPetName(event.target.value)}
                  className="form-control"
                  placeholder="Name"
                  required
                />
              </div>

              <div className="mb-3">
                <label htmlFor="gender"> Gender </label>
                <select
                  selected={gender}
                  onChange={(event) => setGender(event.target.value)}
                  className="form-control"
                >
                  <option value=""></option>
                  <option value="female">female</option>
                  <option value="male">male</option>
                </select>
              </div>

              <div className="mb-3">
                <label htmlFor="birthday"> Birthday </label>
                <input
                  type="date"
                  value={birthday}
                  onChange={(event) => setBirthday(event.target.value)}
                  className="form-control"
                />
              </div>

              <div className="mb-3">
                <label htmlFor="breed"> Breed </label>
                <input
                  type="text"
                  value={breed}
                  onChange={(event) => setBreed(event.target.value)}
                  className="form-control"
                  placeholder="Breed"
                />
              </div>

              <div className="mb-3">
                <label htmlFor="my_file"> Image </label>
                <input
                  type="file"
                  onChange={(event) => setImageFile(event.target.files[0])}
                  className="form-control"
                  accept="image/png, image/jpeg"
                />
              </div>
              <div className="modal-footer">
                <button
                  type="submit"
                  className="btn btn-sm btn-outline-dark btn-block mt-4"
                  data-bs-dismiss="modal"
                  onClick={validatePetProfile}
                >
                  Save
                </button>
                <button
                  type="button"
                  className="btn btn-sm btn-secondary btn-block mt-4"
                  data-bs-dismiss="modal"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </React.Fragment>
  );
};

// All Hikes and Hike Details Pet Profile container component
const PetProfileContainer = React.forwardRef((props, ref) => {
  const [petProfiles, setPetProfiles] = React.useState([]);

  const session_login = document.querySelector("#login").innerText;

  React.useEffect(() => {
    getPetProfiles();
  }, []);

  const getPetProfiles = () => {
    if (session_login === "True") {
      fetch("/pets.json")
        .then((response) => response.json())
        .then((data) => {
          setPetProfiles(data.petProfiles);
        });
    }
  };

  // Access getPetProfiles function from Footer component
  React.useImperativeHandle(ref, () => ({
    getPetProfiles() {
      if (session_login === "True") {
        fetch("/pets.json")
          .then((response) => response.json())
          .then((data) => {
            setPetProfiles(data.petProfiles);
          });
      }
    },
  }));

  const allPetProfiles = [];
  const allEditPetProfiles = [];

  for (const currentPetProfile of petProfiles) {
    let initial_miles = 0;
    let total_miles = currentPetProfile.check_ins.reduce(function (
      previousValue,
      currentValue
    ) {
      return previousValue + currentValue.miles_completed;
    },
    initial_miles);

    if (
      currentPetProfile.birthday !== null &&
      currentPetProfile.birthday !== ""
    ) {
      const birthday = new Date(currentPetProfile.birthday);
      const birthday_formatted = birthday.toLocaleDateString();

      allPetProfiles.push(
        <PetProfile
          key={currentPetProfile.pet_id}
          pet_id={currentPetProfile.pet_id}
          pet_name={currentPetProfile.pet_name}
          gender={currentPetProfile.gender}
          birthday={currentPetProfile.birthday}
          breed={currentPetProfile.breed}
          pet_img_URL={currentPetProfile.pet_img_url}
          check_ins={currentPetProfile.check_ins}
          total_miles={total_miles}
          getPetProfiles={getPetProfiles}
        />
      );
      allEditPetProfiles.push(
        <EditPetProfile
          key={currentPetProfile.pet_id}
          pet_id={currentPetProfile.pet_id}
          pet_name={currentPetProfile.pet_name}
          gender={currentPetProfile.gender}
          birthday={birthday_formatted}
          breed={currentPetProfile.breed}
          getPetProfiles={getPetProfiles}
        />
      );
    } else {
      allPetProfiles.push(
        <PetProfile
          key={currentPetProfile.pet_id}
          pet_id={currentPetProfile.pet_id}
          pet_name={currentPetProfile.pet_name}
          gender={currentPetProfile.gender}
          birthday={currentPetProfile.birthday}
          breed={currentPetProfile.breed}
          pet_img_URL={currentPetProfile.pet_imgURL}
          check_ins={currentPetProfile.check_ins}
          total_miles={total_miles}
          getPetProfiles={getPetProfiles}
        />
      );
      allEditPetProfiles.push(
        <EditPetProfile
          key={currentPetProfile.pet_id}
          pet_id={currentPetProfile.pet_id}
          pet_name={currentPetProfile.pet_name}
          gender={currentPetProfile.gender}
          birthday={currentPetProfile.birthday}
          breed={currentPetProfile.breed}
          getPetProfiles={getPetProfiles}
        />
      );
    }
  }

  return (
    <React.Fragment>
      <AddPetProfile getPetProfiles={getPetProfiles} />
      {allEditPetProfiles}
      <div
        className="offcanvas offcanvas-end"
        style={{ width: "580px" }}
        data-bs-keyboard="true"
        data-bs-scroll="true"
        data-bs-backdrop="true"
        tabIndex="-1"
        id="Profile"
        aria-labelledby="ProfileLabel"
      >
        <div className="offcanvas-header">
          <h3 className="offcanvas-title" id="ProfileLabel">
            Pet Profile
          </h3>
          {session_login === "True" ? (
            <a
              className="btn btn-sm btn-outline-dark fw-300"
              href=""
              data-bs-toggle="modal"
              data-bs-target="#modal-add-pet"
            >
              <i
                data-bs-toggle="tooltip"
                data-bs-placement="right"
                title="add a pet profile"
                className="fa-solid fa-paw"
              ></i>{" "}
              add a pet profile
            </a>
          ) : null}
        </div>
        <div className="offcanvas-body fw-300">
          {session_login !== "True" ? (
            <div className="fw-300">Please log in to add a pet profile.</div>
          ) : (
            <div>
              <div style={{ padding: "0.5em" }}>{allPetProfiles}</div>
            </div>
          )}
          <div
            className="offcanvas-footer"
            style={{
              position: "fixed",
              right: "543px",
              bottom: "10px",
              zIndex: "100",
            }}
          >
            <button
              type="button"
              className="btn-close text-reset"
              data-bs-dismiss="offcanvas"
              aria-label="Close"
            ></button>
          </div>
        </div>
      </div>
    </React.Fragment>
  );
});

// Dashboard Pet Profile container component
const DashboardPetProfileContainer = React.forwardRef((props, ref) => {
  const [petProfiles, setPetProfiles] = React.useState([]);

  const session_login = document.querySelector("#login").innerText;

  React.useEffect(() => {
    getPetProfiles();
  }, []);

  const getPetProfiles = () => {
    if (session_login === "True") {
      fetch("/pets.json")
        .then((response) => response.json())
        .then((data) => {
          setPetProfiles(data.petProfiles);
        });
    }
  };

  React.useImperativeHandle(ref, () => ({
    getPetProfiles() {
      if (session_login === "True") {
        fetch("/pets.json")
          .then((response) => response.json())
          .then((data) => {
            setPetProfiles(data.petProfiles);
          });
      }
    },
  }));

  const allPetProfiles = [];
  const allEditPetProfiles = [];

  for (const currentPetProfile of petProfiles) {
    let initial_miles = 0;
    let total_miles = currentPetProfile.check_ins.reduce(function (
      previousValue,
      currentValue
    ) {
      return previousValue + currentValue.miles_completed;
    },
    initial_miles);

    if (
      currentPetProfile.birthday !== null &&
      currentPetProfile.birthday !== ""
    ) {
      const birthday = new Date(currentPetProfile.birthday);
      const birthday_formatted = birthday.toLocaleDateString();

      allPetProfiles.push(
        <PetProfile
          key={currentPetProfile.pet_id}
          pet_id={currentPetProfile.pet_id}
          pet_name={currentPetProfile.pet_name}
          gender={currentPetProfile.gender}
          birthday={currentPetProfile.birthday}
          breed={currentPetProfile.breed}
          pet_img_URL={currentPetProfile.pet_imgURL}
          check_ins={currentPetProfile.check_ins}
          total_miles={total_miles}
          getPetProfiles={getPetProfiles}
        />
      );
      allEditPetProfiles.push(
        <EditPetProfile
          key={currentPetProfile.pet_id}
          pet_id={currentPetProfile.pet_id}
          pet_name={currentPetProfile.pet_name}
          gender={currentPetProfile.gender}
          birthday={birthday_formatted}
          breed={currentPetProfile.breed}
          getPetProfiles={getPetProfiles}
        />
      );
    } else {
      allPetProfiles.push(
        <PetProfile
          key={currentPetProfile.pet_id}
          pet_id={currentPetProfile.pet_id}
          pet_name={currentPetProfile.pet_name}
          gender={currentPetProfile.gender}
          birthday={currentPetProfile.birthday}
          breed={currentPetProfile.breed}
          pet_img_URL={currentPetProfile.pet_imgURL}
          check_ins={currentPetProfile.check_ins}
          total_miles={total_miles}
          getPetProfiles={getPetProfiles}
        />
      );
      allEditPetProfiles.push(
        <EditPetProfile
          key={currentPetProfile.pet_id}
          pet_id={currentPetProfile.pet_id}
          pet_name={currentPetProfile.pet_name}
          gender={currentPetProfile.gender}
          birthday={currentPetProfile.birthday}
          breed={currentPetProfile.breed}
          getPetProfiles={getPetProfiles}
        />
      );
    }
  }

  return (
    <React.Fragment>
      <AddPetProfile getPetProfiles={getPetProfiles} />
      {allEditPetProfiles}
      <div className="side-bar-profiles d-flex flex-column flex-shrink-0 bg-light">
        <div
          className="header clearfix"
          style={{ paddingLeft: "1em", paddingRight: "1em" }}
        >
          <h3 className="title float-start" id="ProfileLabel">
            Pet Profile
          </h3>
          <a
            className="btn btn-sm btn-outline-dark float-end"
            href=""
            data-bs-toggle="modal"
            data-bs-target="#modal-add-pet"
          >
            <i
              data-bs-toggle="tooltip"
              data-bs-placement="right"
              title="add a pet profile"
              className="fa-solid fa-paw"
            ></i>{" "}
            add a pet profile
          </a>
        </div>
        <div style={{ paddingRight: "1em" }}>{allPetProfiles}</div>
      </div>
    </React.Fragment>
  );
});
